#include "stm32f4xx_hal.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

#define QUEUE_LENGTH    10
#define PRODUCER_DELAY  pdMS_TO_TICKS(500)

static QueueHandle_t data_queue;

static void producer_task(void *param)
{
    uint32_t counter = 0;

    while (1) {
        /* Send incrementing value; drop if queue full (timeout 0) */
        xQueueSend(data_queue, &counter, 0);
        counter++;
        vTaskDelay(PRODUCER_DELAY);
    }
}

static void consumer_task(void *param)
{
    uint32_t received;

    while (1) {
        /* Block indefinitely until data available */
        if (xQueueReceive(data_queue, &received, portMAX_DELAY) == pdTRUE) {
            /* Process received value */
            (void)received;
        }
    }
}

static void SystemClock_Config(void);

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    data_queue = xQueueCreate(QUEUE_LENGTH, sizeof(uint32_t));

    /* Producer: lower priority (1), Consumer: higher priority (2) */
    xTaskCreate(producer_task, "Producer", 256, NULL, 1, NULL);
    xTaskCreate(consumer_task, "Consumer", 256, NULL, 2, NULL);

    vTaskStartScheduler();

    /* Should never reach here */
    while (1);
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
