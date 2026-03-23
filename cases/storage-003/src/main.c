#include <zephyr/kernel.h>
#include <zephyr/fs/fs.h>
#include <zephyr/fs/littlefs.h>

FS_LITTLEFS_DECLARE_DEFAULT_CONFIG(storage);

static struct fs_mount_t lfs_mnt = {
	.type = FS_LITTLEFS,
	.fs_data = &storage,
	.mnt_point = "/lfs",
};

int main(void)
{
	int ret;
	struct fs_file_t file;
	const char *write_buf = "hello";
	char read_buf[8] = {0};
	ssize_t bytes;

	ret = fs_mount(&lfs_mnt);
	if (ret < 0) {
		printk("fs_mount failed: %d\n", ret);
		return ret;
	}

	fs_file_t_init(&file);

	ret = fs_open(&file, "/lfs/test.txt", FS_O_CREATE | FS_O_RDWR);
	if (ret < 0) {
		printk("fs_open failed: %d\n", ret);
		return ret;
	}

	bytes = fs_write(&file, write_buf, strlen(write_buf));
	if (bytes < 0) {
		printk("fs_write failed: %d\n", (int)bytes);
		fs_close(&file);
		return (int)bytes;
	}

	ret = fs_seek(&file, 0, FS_SEEK_SET);
	if (ret < 0) {
		printk("fs_seek failed: %d\n", ret);
		fs_close(&file);
		return ret;
	}

	bytes = fs_read(&file, read_buf, sizeof(read_buf) - 1);
	if (bytes < 0) {
		printk("fs_read failed: %d\n", (int)bytes);
		fs_close(&file);
		return (int)bytes;
	}

	fs_close(&file);

	if (strncmp(write_buf, read_buf, strlen(write_buf)) == 0) {
		printk("LittleFS verify OK: \"%s\"\n", read_buf);
	} else {
		printk("LittleFS verify FAIL: wrote \"%s\", read \"%s\"\n",
		       write_buf, read_buf);
		return -EIO;
	}

	return 0;
}
