"""Behavioral checks for linux-userspace-006 (spidev UAPI discipline)."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    has_api_call,
    scoped_contains,
    strip_comments,
)
from embedeval.models import CheckDetail
from embedeval.check_utils import expand_string_defines


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []
    stripped = strip_comments(generated_code)

    # 1. Opens /dev/spidev0.0 with O_RDWR.
    # `#define SPI_DEVICE "/dev/spidev0.0"` + open(SPI_DEVICE, O_RDWR) is the
    # same call; inline string macros before matching the literal.
    expanded = expand_string_defines(stripped)
    has_open_rdwr = bool(
        re.search(
            r'open\s*\(\s*"/dev/spidev0\.0"\s*,\s*O_RDWR\b',
            expanded,
        )
    )
    details.append(
        CheckDetail(
            check_name="open_spidev0_0_rdwr",
            passed=has_open_rdwr,
            expected='open("/dev/spidev0.0", O_RDWR)',
            actual="present" if has_open_rdwr else "missing",
            check_type="constraint",
        )
    )

    # 2. SPI_IOC_WR_MODE ioctl (sets mode BEFORE transfer).
    has_wr_mode = bool(
        re.search(r"SPI_IOC_WR_MODE\b", stripped)
    )
    details.append(
        CheckDetail(
            check_name="spi_ioc_wr_mode_used",
            passed=has_wr_mode,
            expected="SPI_IOC_WR_MODE ioctl (configure mode)",
            actual="present" if has_wr_mode else "missing",
            check_type="constraint",
        )
    )

    # 3. SPI_IOC_WR_BITS_PER_WORD.
    has_bpw = bool(re.search(r"SPI_IOC_WR_BITS_PER_WORD\b", stripped))
    details.append(
        CheckDetail(
            check_name="spi_ioc_wr_bits_per_word_used",
            passed=has_bpw,
            expected="SPI_IOC_WR_BITS_PER_WORD ioctl",
            actual="present" if has_bpw else "missing",
            check_type="constraint",
        )
    )

    # 4. SPI_IOC_WR_MAX_SPEED_HZ.
    has_speed = bool(re.search(r"SPI_IOC_WR_MAX_SPEED_HZ\b", stripped))
    details.append(
        CheckDetail(
            check_name="spi_ioc_wr_max_speed_hz_used",
            passed=has_speed,
            expected="SPI_IOC_WR_MAX_SPEED_HZ ioctl",
            actual="present" if has_speed else "missing",
            check_type="constraint",
        )
    )

    # 5. struct spi_ioc_transfer declared.
    has_struct = "struct spi_ioc_transfer" in stripped
    details.append(
        CheckDetail(
            check_name="spi_ioc_transfer_struct_used",
            passed=has_struct,
            expected="struct spi_ioc_transfer declared",
            actual="present" if has_struct else "missing",
            check_type="constraint",
        )
    )

    # 6. tx_buf AND rx_buf cast to (unsigned long).
    tx_cast_ok = bool(
        re.search(r"\.tx_buf\s*=\s*\(\s*unsigned\s+long\s*\)", stripped)
    )
    rx_cast_ok = bool(
        re.search(r"\.rx_buf\s*=\s*\(\s*unsigned\s+long\s*\)", stripped)
    )
    details.append(
        CheckDetail(
            check_name="tx_rx_buf_cast_to_unsigned_long",
            passed=tx_cast_ok and rx_cast_ok,
            expected="both .tx_buf and .rx_buf assigned via (unsigned long) cast",
            actual=f"tx_cast={tx_cast_ok}, rx_cast={rx_cast_ok}",
            check_type="constraint",
        )
    )

    # 7. SPI_IOC_MESSAGE(1) — NOT SPI_IOC_MESSAGE(0).
    has_msg_1 = bool(re.search(r"SPI_IOC_MESSAGE\s*\(\s*1\s*\)", stripped))
    has_msg_0 = bool(re.search(r"SPI_IOC_MESSAGE\s*\(\s*0\s*\)", stripped))
    details.append(
        CheckDetail(
            check_name="spi_ioc_message_nonzero_count",
            passed=has_msg_1 and not has_msg_0,
            expected="SPI_IOC_MESSAGE(1) for a single-transfer ioctl",
            actual=f"MESSAGE(1)={has_msg_1}, MESSAGE(0)={has_msg_0}",
            check_type="constraint",
        )
    )

    # 8. close(fd) called on the exit path.
    has_close = has_api_call(stripped, "close")
    details.append(
        CheckDetail(
            check_name="close_called",
            passed=has_close,
            expected="close(fd) called",
            actual="present" if has_close else "missing",
            check_type="constraint",
        )
    )

    # 9. perror or fprintf(stderr, ...) on failure paths.
    has_perror = has_api_call(stripped, "perror") or bool(
        re.search(r"fprintf\s*\(\s*stderr", stripped)
    )
    details.append(
        CheckDetail(
            check_name="perror_on_failure",
            passed=has_perror,
            expected="perror() or fprintf(stderr, ...) used on ioctl failure",
            actual="present" if has_perror else "missing",
            check_type="constraint",
        )
    )

    # 10. No Arduino SPI.transfer / SPI.begin.
    has_arduino = bool(re.search(r"\bSPI\.\s*(transfer|begin)\s*\(", stripped))
    details.append(
        CheckDetail(
            check_name="no_arduino_spi_api",
            passed=not has_arduino,
            expected="No Arduino SPI.transfer() / SPI.begin()",
            actual="clean" if not has_arduino else "WRONG: Arduino API",
            check_type="constraint",
        )
    )

    # 11. Does NOT fall back to write()/read() on the fd for the transaction.
    # write/read on spidev fd is a legacy half-duplex shortcut; the ioctl
    # transaction is required for simultaneous TX+RX.
    # Match write(fd, ...) and read(fd, ...) patterns; the reference uses
    # close(fd) which must NOT match here.
    has_write_fd = bool(re.search(r"\bwrite\s*\(\s*fd\s*,", stripped))
    has_read_fd = bool(re.search(r"\bread\s*\(\s*fd\s*,", stripped))
    details.append(
        CheckDetail(
            check_name="no_write_read_fallback",
            passed=not (has_write_fd or has_read_fd),
            expected="No write(fd,...)/read(fd,...) on spidev — use ioctl transfer",
            actual=(
                f"write={has_write_fd}, read={has_read_fd}"
                if (has_write_fd or has_read_fd)
                else "clean"
            ),
            check_type="constraint",
        )
    )

    # 12. Speed set to 1_000_000 somewhere (either as direct value or macro
    # that resolves to it).
    has_speed_1m = bool(
        re.search(r"\b1000000\b|\b1_000_000\b|\b1000000u?\b|\b1000000U\b", stripped)
    )
    details.append(
        CheckDetail(
            check_name="speed_1mhz_configured",
            passed=has_speed_1m,
            expected="Speed = 1_000_000 (1 MHz) per prompt",
            actual="present" if has_speed_1m else "missing",
            check_type="constraint",
        )
    )

    # 13. No cross-platform APIs.
    cross_plat = check_no_cross_platform_apis(
        generated_code, skip_platforms=["Linux_Userspace", "POSIX"]
    )
    details.append(
        CheckDetail(
            check_name="no_cross_platform_apis",
            passed=len(cross_plat) == 0,
            expected="No FreeRTOS / Zephyr / Arduino / STM32 HAL APIs",
            actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
            check_type="constraint",
        )
    )

    return details
