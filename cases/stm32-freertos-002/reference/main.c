#include "stm32f4xx_hal.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

/*
 * TIM2 generates an interrupt at 10Hz (every 100ms).
 * ISR uses xQueueSendFromISR — the ISR-safe variant.
 * The receiving task blocks on xQueueReceive with portMAX_DELAY.
 * NEVER call xQueueSend (blocking) from an ISR — undefined behavior.
 */

TIM_HandleTypeDef htim2;
static QueueHandle_t isr_queue;
static uint32_t isr_counter = 0;

static void SystemClock_Config(void);
static void MX_TIM2_Init(void);

static void receiver_task(void *param)
{
    uint32_t value;

    while (1) {
        /* Block until ISR sends data */
        if (xQueueReceive(isr_queue, &value, portMAX_DELAY) == pdTRUE) {
            /* Process data from ISR */
            (void)value;
        }
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_TIM2_Init();

    isr_queue = xQueueCreate(10, sizeof(uint32_t));

    xTaskCreate(receiver_task, "Receiver", 256, NULL, 2, NULL);

    HAL_TIM_Base_Start_IT(&htim2);

    vTaskStartScheduler();

    while (1);
}

/* TIM2 period elapsed callback — called from ISR context */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM2) {
        BaseType_t higher_priority_woken = pdFALSE;

        isr_counter++;
        /* ISR-safe queue send — MUST use FromISR variant */
        xQueueSendFromISR(isr_queue, &isr_counter, &higher_priority_woken);

        /* Yield to higher-priority task if woken */
        portYIELD_FROM_ISR(higher_priority_woken);
    }
}

void TIM2_IRQHandler(void)
{
    HAL_TIM_IRQHandler(&htim2);
}

static void MX_TIM2_Init(void)
{
    __HAL_RCC_TIM2_CLK_ENABLE();

    /*
     * 10Hz interrupt at 84MHz APB1 timer clock:
     * PSC = 8399 → tick = 84MHz/8400 = 10kHz
     * ARR = 999  → period = 10kHz/1000 = 10Hz
     */
    htim2.Instance               = TIM2;
    htim2.Init.Prescaler         = 8399;
    htim2.Init.CounterMode       = TIM_COUNTERMODE_UP;
    htim2.Init.Period            = 999;
    htim2.Init.ClockDivision     = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    HAL_TIM_Base_Init(&htim2);

    HAL_NVIC_SetPriority(TIM2_IRQn, 6, 0); /* Must be >= configMAX_SYSCALL_INTERRUPT_PRIORITY */
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
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
