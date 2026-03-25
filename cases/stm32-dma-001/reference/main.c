#include "stm32f4xx_hal.h"
#include <string.h>

#define TRANSFER_SIZE 256

DMA_HandleTypeDef hdma2_stream0;

/* Buffers must be accessible by DMA — global/static ensures correct placement */
static uint8_t src_buf[TRANSFER_SIZE];
static uint8_t dst_buf[TRANSFER_SIZE];
static volatile uint8_t transfer_done  = 0;
static volatile uint8_t transfer_error = 0;

static void SystemClock_Config(void);
static void MX_DMA_Init(void);

/* DMA transfer complete callback */
void HAL_DMA_XferCpltCallback(DMA_HandleTypeDef *hdma)
{
    if (hdma->Instance == DMA2_Stream0) {
        transfer_done = 1;
    }
}

/* DMA error callback */
void HAL_DMA_XferErrorCallback(DMA_HandleTypeDef *hdma)
{
    if (hdma->Instance == DMA2_Stream0) {
        transfer_error = 1;
    }
}

void DMA2_Stream0_IRQHandler(void)
{
    HAL_DMA_IRQHandler(&hdma2_stream0);
}

int main(void)
{
    HAL_StatusTypeDef status;

    HAL_Init();
    SystemClock_Config();
    MX_DMA_Init();

    /* Fill source buffer with test pattern */
    for (int i = 0; i < TRANSFER_SIZE; i++) {
        src_buf[i] = (uint8_t)i;
    }
    memset(dst_buf, 0, sizeof(dst_buf));

    /* Register callbacks */
    HAL_DMA_RegisterCallback(&hdma2_stream0, HAL_DMA_XFER_CPLT_CB_ID,  HAL_DMA_XferCpltCallback);
    HAL_DMA_RegisterCallback(&hdma2_stream0, HAL_DMA_XFER_ERROR_CB_ID, HAL_DMA_XferErrorCallback);

    /* Start DMA transfer with interrupt */
    status = HAL_DMA_Start_IT(&hdma2_stream0,
                               (uint32_t)src_buf,
                               (uint32_t)dst_buf,
                               TRANSFER_SIZE);
    if (status != HAL_OK) {
        /* Configuration error */
        while (1);
    }

    /* Wait for completion */
    while (!transfer_done && !transfer_error);

    if (transfer_error) {
        /* DMA error occurred */
        while (1);
    }

    /* Verify transferred data */
    if (memcmp(src_buf, dst_buf, TRANSFER_SIZE) == 0) {
        /* Transfer successful */
        (void)0;
    } else {
        /* Data mismatch */
        while (1);
    }

    while (1) {
        /* Application loop */
    }
}

static void MX_DMA_Init(void)
{
    __HAL_RCC_DMA2_CLK_ENABLE();

    hdma2_stream0.Instance                 = DMA2_Stream0;
    hdma2_stream0.Init.Channel             = DMA_CHANNEL_0;
    hdma2_stream0.Init.Direction           = DMA_MEMORY_TO_MEMORY;
    hdma2_stream0.Init.PeriphInc           = DMA_PINC_ENABLE;   /* Src pointer increments */
    hdma2_stream0.Init.MemInc              = DMA_MINC_ENABLE;   /* Dst pointer increments */
    hdma2_stream0.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma2_stream0.Init.MemDataAlignment    = DMA_MDATAALIGN_BYTE;
    hdma2_stream0.Init.Mode                = DMA_NORMAL;
    hdma2_stream0.Init.Priority            = DMA_PRIORITY_HIGH;
    hdma2_stream0.Init.FIFOMode            = DMA_FIFOMODE_ENABLE;
    hdma2_stream0.Init.FIFOThreshold       = DMA_FIFO_THRESHOLD_FULL;
    hdma2_stream0.Init.MemBurst            = DMA_MBURST_SINGLE;
    hdma2_stream0.Init.PeriphBurst         = DMA_PBURST_SINGLE;
    HAL_DMA_Init(&hdma2_stream0);

    HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
}

static void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState       = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState   = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource  = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM       = 8;
    RCC_OscInitStruct.PLL.PLLN       = 336;
    RCC_OscInitStruct.PLL.PLLP       = RCC_PLLP_DIV2;
    RCC_OscInitStruct.PLL.PLLQ       = 7;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);

    RCC_ClkInitStruct.ClockType      = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                                     | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5);
}
