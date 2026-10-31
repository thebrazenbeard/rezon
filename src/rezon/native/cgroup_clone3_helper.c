/*
 * A deliberately small, host-installed Linux launcher for Rezon.
 *
 * Usage: helper CGROUP_LEAF PAYLOAD_UID PAYLOAD_GID -- /absolute/exe [args ...]
 * The host supplies REZON_READY_FD as a pre-opened pipe FD. The trusted parent
 * must withhold all request bytes until it has received and checked that PID.
 * The payload enters its cgroup AT CLONE via CLONE_INTO_CGROUP; attaching an
 * already running PID is forbidden. No shell interpretation is performed.
 *
 * This helper must be provisioned as a protected OS-owned executable. Source
 * review alone cannot authenticate that installation or the cgroup delegation.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <limits.h>
#include <linux/sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#ifndef CLONE_INTO_CGROUP
#define CLONE_INTO_CGROUP (1ULL << 33)
#endif

static int parse_id(const char *input, uid_t *output) {
    char *end = NULL;
    errno = 0;
    unsigned long n = strtoul(input, &end, 10);
    if (errno || end == input || *end || n == 0 || n > UINT32_MAX) return -1;
    *output = (uid_t)n;
    return -((unsigned long)*output != n);
}

static int write_all(int fd, const char *buf, size_t len) {
    while (len) {
        ssize_t n = write(fd, buf, len);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) return -1;
        buf += n;
        len -= (size_t)n;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 6 || strcmp(argv[4], "--") != 0 || argv[5][0] != '/') {
        fprintf(stderr, "invalid trusted launch arguments\n");
        return 126;
    }
    uid_t uid, gid;
    if (parse_id(argv[2], &uid) || parse_id(argv[3], &gid) || uid == geteuid()) {
        fprintf(stderr, "unseparated or invalid payload identity\n");
        return 126;
    }
    const char *fdtext = getenv("REZON_READY_FD");
    if (!fdtext || !*fdtext) return 126;
    char *end = NULL;
    errno = 0;
    long ready = strtol(fdtext, &end, 10);
    if (errno || end == fdtext || *end || ready < 3 || ready > INT_MAX) return 126;
    int cfd = open(argv[1], O_DIRECTORY | O_NOFOLLOW | O_RDONLY | O_CLOEXEC);
    if (cfd < 0) {
        perror("open delegated cgroup");
        return 126;
    }
    struct clone_args clone_params = {0};
    clone_params.flags = CLONE_INTO_CGROUP;
    clone_params.cgroup = (uint64_t)cfd;
    clone_params.exit_signal = SIGCHLD;
    pid_t pid = (pid_t)syscall(SYS_clone3, &clone_params, sizeof(clone_params));
    if (pid < 0) {
        /* ENOSYS, EINVAL, EACCES, EPERM, EBUSY and EOPNOTSUPP all fail shut. */
        perror("clone3(CLONE_INTO_CGROUP)");
        close(cfd);
        return 126;
    }
    if (pid == 0) {
        /* No payload exec is possible until kernel placement has succeeded. */
        close(cfd);
        close((int)ready);
        unsetenv("REZON_READY_FD");
        if (setgroups(0, NULL) || setgid(gid) || setuid(uid)) _exit(126);
        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) _exit(126);
        execv(argv[5], &argv[5]);
        _exit(127);
    }
    char ready_line[64];
    int n = snprintf(ready_line, sizeof(ready_line), "%ld\n", (long)pid);
    if (n <= 0 || (size_t)n >= sizeof(ready_line) ||
        write_all((int)ready, ready_line, (size_t)n)) {
        int killfd = openat(cfd, "cgroup.kill", O_WRONLY | O_CLOEXEC | O_NOFOLLOW);
        if (killfd >= 0) {
            (void)write_all(killfd, "1\n", 2);
            close(killfd);
        }
        kill(pid, SIGKILL);
        waitpid(pid, NULL, 0);
        close(cfd);
        return 126;
    }
    close(cfd);
    close((int)ready);
    int status = 0;
    while (waitpid(pid, &status, 0) < 0) {
        if (errno == EINTR) continue;
        return 126;
    }
    if (WIFEXITED(status)) return WEXITSTATUS(status);
    if (WIFSIGNALED(status)) return 128 + WTERMSIG(status);
    return 126;
}
