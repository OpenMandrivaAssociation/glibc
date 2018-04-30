#include <sys/types.h>
#include <sys/wait.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <sys/time.h>
#include <dirent.h>
#include <stddef.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include <elf.h>

#define LD_SO_CONF "/etc/ld.so.conf"
#define ICONVCONFIG "/usr/sbin/iconvconfig"

#define verbose_exec(failcode, path...) \
  do							\
    {							\
      char *const arr[] = { path, NULL };		\
      vexec (failcode, arr);				\
    } while (0)

__attribute__((noinline)) void vexec (int failcode, char *const path[]);
__attribute__((noinline)) void says (const char *str);
__attribute__((noinline)) void sayn (long num);
__attribute__((noinline)) void message (char *const path[]);
__attribute__((noinline)) int check_elf (const char *name);

int
main (void)
{
  struct stat statbuf;
  char initpath[256];

  char buffer[4096];
  struct pref {
    char *p;
    int len;
  } prefix[] = { { "libc-", 5 }, { "libm-", 5 },
		 { "librt-", 6 }, { "libpthread-", 11 },
		 { "librtkaio-", 10 }, { "libthread_db-", 13 } };
  int i, j, fd;
  off_t base;
  ssize_t ret;

  /* In order to support in-place upgrades, we must immediately remove
     obsolete platform directories after installing a new glibc
     version.  RPM only deletes files removed by updates near the end
     of the transaction.  If we did not remove the obsolete platform
     directories here, they would be preferred by the dynamic linker
     during the execution of subsequent RPM scriptlets, likely
     resulting in process startup failures.  */
  const char *remove_dirs[] =
    {
#if defined (__i386__)
      "/lib/i686",
      "/lib/i686/nosegneg",
#elif defined (__powerpc64__) && _CALL_ELF != 2
      "/lib64/power6",
#endif
    };
  for (j = 0; j < sizeof (remove_dirs) / sizeof (remove_dirs[0]); ++j)
    {
      size_t rmlen = strlen (remove_dirs[j]);
      fd = open (remove_dirs[j], O_RDONLY);
      if (fd >= 0
	  && (ret = getdirentries (fd, buffer, sizeof (buffer), &base))
	     >= (ssize_t) offsetof (struct dirent, d_name))
	{
	  for (base = 0; base + offsetof (struct dirent, d_name) < ret; )
	    {
	      struct dirent *d = (struct dirent *) (buffer + base);

	      for (i = 0; i < sizeof (prefix) / sizeof (prefix[0]); i++)
		if (! strncmp (d->d_name, prefix[i].p, prefix[i].len))
		  {
		    char *p = d->d_name + prefix[i].len;

		    while (*p == '.' || (*p >= '0' && *p <= '9')) p++;
		    if (p[0] == 's' && p[1] == 'o' && p[2] == '\0'
			&& p + 3 - d->d_name
			   < sizeof (initpath) - rmlen - 1)
		      {
			memcpy (initpath, remove_dirs[j], rmlen);
			initpath[rmlen] = '/';
			strcpy (initpath + rmlen + 1, d->d_name);
			unlink (initpath);
			break;
		      }
		  }
	      base += d->d_reclen;
	    }
	  close (fd);
	}
    }

  int ldsocfd = open (LD_SO_CONF, O_RDONLY);
  struct stat ldsocst;
  if (ldsocfd >= 0 && fstat (ldsocfd, &ldsocst) >= 0)
    {
      char p[ldsocst.st_size + 1];
      if (read (ldsocfd, p, ldsocst.st_size) == ldsocst.st_size)
	{
	  p[ldsocst.st_size] = '\0';
	  if (strstr (p, "include ld.so.conf.d/*.conf") == NULL)
	    {
	      close (ldsocfd);
	      ldsocfd = open (LD_SO_CONF, O_WRONLY | O_TRUNC);
	      if (ldsocfd >= 0)
		{
		  size_t slen = strlen ("include ld.so.conf.d/*.conf\n");
		  if (write (ldsocfd, "include ld.so.conf.d/*.conf\n", slen)
		      != slen
		      || write (ldsocfd, p, ldsocst.st_size) != ldsocst.st_size)
		    _exit (109);
		}
	    }
	}
      if (ldsocfd >= 0)
	close (ldsocfd);
    }

  /* If installing bi-arch glibc, rpm sometimes doesn't unpack all files
     before running one of the lib's %post scriptlet.  /sbin/ldconfig will
     then be run by the other arch's %post.  */
  if (! access ("/sbin/ldconfig", X_OK))
    verbose_exec (110, "/sbin/ldconfig", "/sbin/ldconfig", "-X");

  if (! utimes (GCONV_MODULES_DIR "/gconv-modules.cache", NULL))
    {
    char *iconv_cache = GCONV_MODULES_DIR"/gconv-modules.cache";
    char *iconv_dir = GCONV_MODULES_DIR;
    verbose_exec (113, ICONVCONFIG, "/usr/sbin/iconvconfig",
	    "-o", iconv_cache,
	    "--nostdlib", iconv_dir);
    }

  /* Check if systemctl is available for further systemd deamon restart*/
  if (access ("/bin/systemctl", X_OK))
    _exit (0);

  /* Check if we are not inside of some chroot, because we'd just
     timeout and leave /etc/initrunlvl.

     On more modern systems this test is not sufficient to detect
     if we're in a chroot.  */
  if (readlink ("/proc/1/exe", initpath, 256) <= 0 ||
      readlink ("/proc/1/root", initpath, 256) <= 0)
    _exit (0);

  /* Here's another well known way to detect chroot, at least on an
     ext and xfs filesystems and assuming nothing mounted on the chroot's
     root. 
      # (tpg) Possible 2017 solutions
      # 1. check if inode for "/" is in 0 between 4096 range,
      #    as this may get into account almost all firesystems?
      # 2. check if /proc/1/cgroup output does contain word docker or lxc
      #
  if (stat ("/", &statbuf) != 0
      || (statbuf.st_ino != 2
	  && statbuf.st_ino != 128))
    _exit (0); */

  if (check_elf ("/proc/1/exe"))
    verbose_exec (116, "/bin/systemctl", "/bin/systemctl", "daemon-reexec");

  /* Check if we can safely condrestart sshd.  */
  if (access ("/bin/systemctl", X_OK) == 0
      && access ("/usr/sbin/sshd", X_OK) == 0
      && access ("/bin/sh", F_OK) == 0)
    {
      if (check_elf ("/usr/sbin/sshd"))
	verbose_exec (-121, "/bin/systemctl", "/bin/systemctl", "-q", "try-restart", "sshd.service");
    }

  _exit(0);
}

void
vexec (int failcode, char *const path[])
{
  pid_t pid;
  int status, save_errno;
  int devnull = 0;

  if (failcode < 0)
    {
      devnull = 1;
      failcode = -failcode;
    }
  pid = vfork ();
  if (pid == 0)
    {
      int fd;
      if (devnull && (fd = open ("/dev/null", O_WRONLY)) >= 0)
	{
	  dup2 (fd, 1);
	  dup2 (fd, 2);
	  close (fd);
	}
      execv (path[0], path + 1);
      save_errno = errno;
      message (path);
      says (" exec failed with errno ");
      sayn (save_errno);
      says ("\n");
      _exit (failcode);
    }
  else if (pid < 0)
    {
      save_errno = errno;
      message (path);
      says (" fork failed with errno ");
      sayn (save_errno);
      says ("\n");
      _exit (failcode + 1);
    }
  if (waitpid (0, &status, 0) != pid || !WIFEXITED (status))
    {
      message (path);
      says (" child terminated abnormally\n");
      _exit (failcode + 2);
    }
  if (WEXITSTATUS (status))
    {
      message (path);
      says (" child exited with exit code ");
      sayn (WEXITSTATUS (status));
      says ("\n");
      _exit (WEXITSTATUS (status));
    }
}

void
says (const char *str)
{
  write (1, str, strlen (str));
}

void
sayn (long num)
{
  char string[sizeof (long) * 3 + 1];
  char *p = string + sizeof (string) - 1;

  *p = '\0';
  if (num == 0)
    *--p = '0';
  else
    while (num)
      {
	*--p = '0' + num % 10;
	num = num / 10;
      }

  says (p);
}

void
message (char *const path[])
{
  says ("/usr/sbin/glibc_post_upgrade: While trying to execute ");
  says (path[0]);
}

int
check_elf (const char *name)
{
  /* Play safe, if we can't open or read, assume it might be
     ELF for the current arch.  */
  int ret = 1;
  int fd = open (name, O_RDONLY);
  if (fd >= 0)
    {
      Elf32_Ehdr ehdr;
      if (read (fd, &ehdr, offsetof (Elf32_Ehdr, e_version))
	  == offsetof (Elf32_Ehdr, e_version))
	{
	  ret = 0;
	  if (ehdr.e_ident[EI_CLASS]
	      == (sizeof (long) == 8 ? ELFCLASS64 : ELFCLASS32))
	    {
#if defined __i386__
	      ret = ehdr.e_machine == EM_386;
#elif defined __x86_64__
	      ret = ehdr.e_machine == EM_X86_64;
#elif defined __powerpc64__
	      ret = ehdr.e_machine == EM_PPC64;
#elif defined __powerpc__
	      ret = ehdr.e_machine == EM_PPC;
#elif defined __s390__ || defined __s390x__
	      ret = ehdr.e_machine == EM_S390;
#elif defined __x86_64__
	      ret = ehdr.e_machine == EM_X86_64;
#elif defined __sparc__
	      if (sizeof (long) == 8)
		ret = ehdr.e_machine == EM_SPARCV9;
	      else
		ret = (ehdr.e_machine == EM_SPARC
		       || ehdr.e_machine == EM_SPARC32PLUS);
#else
	      ret = 1;
#endif
	    }
	}
      close (fd);
    }
  return ret;
}
