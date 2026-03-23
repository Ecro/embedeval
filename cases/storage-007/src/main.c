#include <zephyr/kernel.h>
#include <zephyr/fs/fs.h>
#include <zephyr/fs/littlefs.h>
#include <zephyr/storage/flash_map.h>

#define STORAGE_PARTITION storage_partition
#define STORAGE_PARTITION_ID FIXED_PARTITION_ID(STORAGE_PARTITION)

FS_LITTLEFS_DECLARE_DEFAULT_CONFIG(cstorage);

static struct fs_mount_t lfs_mount = {
	.type = FS_LITTLEFS,
	.fs_data = &cstorage,
	.storage_dev = (void *)STORAGE_PARTITION_ID,
	.mnt_point = "/lfs",
};

int main(void)
{
	int ret;
	struct fs_file_t file;

	ret = fs_mount(&lfs_mount);
	if (ret < 0) {
		printk("Mount failed (%d), formatting...\n", ret);

		ret = fs_mkfs(FS_LITTLEFS, (uintptr_t)STORAGE_PARTITION_ID,
			      NULL, 0);
		if (ret < 0) {
			printk("Format failed: %d\n", ret);
			return ret;
		}

		ret = fs_mount(&lfs_mount);
		if (ret < 0) {
			printk("Remount failed: %d\n", ret);
			return ret;
		}
	}

	printk("FS MOUNTED OK\n");

	/* Write a test file to verify filesystem is functional */
	fs_file_t_init(&file);
	ret = fs_open(&file, "/lfs/test.txt",
		      FS_O_CREATE | FS_O_WRITE | FS_O_TRUNC);
	if (ret < 0) {
		printk("fs_open failed: %d\n", ret);
		return ret;
	}

	const char *msg = "hello";
	ret = fs_write(&file, msg, strlen(msg));
	if (ret < 0) {
		printk("fs_write failed: %d\n", ret);
		fs_close(&file);
		return ret;
	}

	fs_close(&file);
	printk("Test file written OK\n");

	return 0;
}
