/**
 * Copyright (c) 2020 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include "pico/stdlib.h"
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/spi.h"
#include <hardware/dma.h>
#include <string.h>
#include "top.h"
#include "bottom.h"

#include "frame.h"



#include <stdio.h>
#include "pico/stdlib.h"


#define MEMLCD_CS_PIN 13
#define MEMLCD_SPI spi1
#define MEMLCD_SCK_PIN 14
#define MEMLCD_DI_PIN 15
#define MEMLCD_DISP_PIN 28
#define MEMLCD_EXTCOM_PIN 29

#define FLP_ENABLE_PIN 8
#define FLP_ISET_PIN 6
#define N_FLP_LEVELS 2
#define FLP_DFEAULT_LEVEL 1
const static int flp_levels[N_FLP_LEVELS] = {0, 100};

#define BTN_PREV_PIN 0
#define BTN_NEXT_PIN 2
#define BTN_MAIN_PIN 7 // Azumo Button




#define LCD_WIDTH 272
#define LCD_HEIGHT 451


static void send_pixels_start(int ln);
static void send_pixels_finish();
static void clear();

static uint8_t display_buf[LCD_WIDTH];


static uint8_t __attribute__((aligned(4))) line_buf_a[204 + 2 + 2 + 2];
static uint8_t __attribute__((aligned(4))) line_buf_b[204 + 2 + 2 + 2];
static uint8_t* line_buf = line_buf_a;

static uint32_t dma_tx;
static dma_channel_config dma_conf;

void LCD_init()
{
	// Initialize CS
	gpio_init(MEMLCD_CS_PIN);
	gpio_set_dir(MEMLCD_CS_PIN, GPIO_OUT);
	gpio_put(MEMLCD_CS_PIN, 0);

	// Initialize DISP
	gpio_init(MEMLCD_DISP_PIN);
	gpio_set_dir(MEMLCD_DISP_PIN, GPIO_OUT);
	gpio_put(MEMLCD_DISP_PIN, 0);

	// Initialize extcom as a 100 hertz square wave
	gpio_set_function(MEMLCD_EXTCOM_PIN, GPIO_FUNC_PWM);
	uint slice_num = pwm_gpio_to_slice_num(MEMLCD_EXTCOM_PIN);
	pwm_set_clkdiv(slice_num, 250.f); // Starting from 125MHz system clock, divide by 250
	pwm_set_wrap(slice_num, 5000);    // And then 5000
	pwm_set_chan_level(slice_num, pwm_gpio_to_channel(MEMLCD_EXTCOM_PIN), 2500);
	pwm_set_enabled(slice_num, true);

	// Initialize SPI at 7MHZ
	spi_init(MEMLCD_SPI, 7000000);
	spi_set_format(MEMLCD_SPI, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
	gpio_set_function(MEMLCD_SCK_PIN, GPIO_FUNC_SPI);
	gpio_set_function(MEMLCD_DI_PIN, GPIO_FUNC_SPI);

	// Initialize DMA
	dma_tx   = dma_claim_unused_channel(true);
	dma_conf = dma_channel_get_default_config(dma_tx);
	channel_config_set_transfer_data_size(&dma_conf, DMA_SIZE_8);
	channel_config_set_dreq(&dma_conf, spi_get_dreq(MEMLCD_SPI, true));

	// Clear LCD
	clear();

	// Enable LCD
	gpio_put(MEMLCD_DISP_PIN, 1);
}

static void clear()
{
	for (int i = 0; i < LCD_WIDTH; i++) {
		display_buf[i] = 0;
	}
	for (int i = 0; i < LCD_HEIGHT; i++) {
		send_pixels_finish();
		send_pixels_start(i);
		line_buf = (line_buf == line_buf_a) ? line_buf_b : line_buf_a;
	}
}

uint8_t LCD_color(uint8_t rgb6)
{
	// Input  pixel format: xxRrGgBb
	// Output pixel format: xxRGBrgb

	uint8_t packed = 0;

	packed |= rgb6 & (1 << 5) >> 0; // R
	packed |= rgb6 & (1 << 4) >> 2; // r
	packed |= rgb6 & (1 << 3) << 1; // G
	packed |= rgb6 & (1 << 2) >> 1; // g
	packed |= rgb6 & (1 << 1) << 2; // B
	packed |= rgb6 & (1 << 0) >> 0; // b

	return packed;
}

static int f = 0;

void Top()
{
	for (int line = 0; line < TOP_HEIGHT; line++) 
    {
		int l  = 0;
		memcpy(display_buf,&top[ line * TOP_WIDTH],TOP_WIDTH);
			
		send_pixels_finish();
		send_pixels_start(line);

		line_buf = (line_buf == line_buf_a) ? line_buf_b : line_buf_a;
	}

}

void Bottom()
{
	for (int line = 0; line < BOTTOM_HEIGHT; line++) 
    {
		int l  = 0;
		memcpy(display_buf,&bottom[line * BOTTOM_WIDTH],BOTTOM_WIDTH);
			
		send_pixels_finish();
		send_pixels_start(LCD_HEIGHT- (BOTTOM_HEIGHT) + line);

		line_buf = (line_buf == line_buf_a) ? line_buf_b : line_buf_a;
	}

}


void LCD_update()
{
	
	f++;

	if(f>=FRAME_FRAME_COUNT)
		f = 0;	
  
	for (int line = 0; line < FRAME_HEIGHT; line++) 
    {
		//if (!updated_lines[line])
		//	continue;

		int l  = 0;


		memcpy(display_buf,&frame[f*(FRAME_WIDTH*FRAME_HEIGHT) + line * FRAME_WIDTH],FRAME_WIDTH);
			

		send_pixels_finish();
		send_pixels_start(line + (LCD_HEIGHT - FRAME_HEIGHT) / 2);

		line_buf = (line_buf == line_buf_a) ? line_buf_b : line_buf_a;
	}
}


void LCD_fill()
{
	f++;

	if(f>=FRAME_FRAME_COUNT)
		f = 0;	
  
	for (int line = 0; line < LCD_HEIGHT; line++) 
    {
		//if (!updated_lines[line])
		//	continue;

		int l  = 0;

		memset(display_buf,0,FRAME_WIDTH);
		
		send_pixels_finish();
		send_pixels_start(line);

		line_buf = (line_buf == line_buf_a) ? line_buf_b : line_buf_a;
	}
}

void LCD_update_landscape()
{
	f++;

	if(f>=FRAME_FRAME_COUNT)
		f = 0;	
  
	for (int line = 0; line < FRAME_HEIGHT; line++) 
    {
		//if (!updated_lines[line])
		//	continue;

		int l  = 0;


		memcpy(display_buf,&frame[f*(FRAME_WIDTH*FRAME_HEIGHT) + line * FRAME_WIDTH],FRAME_WIDTH);
		
		send_pixels_finish();
		send_pixels_start(line + (LCD_HEIGHT-FRAME_HEIGHT)/2);

		line_buf = (line_buf == line_buf_a) ? line_buf_b : line_buf_a;
	}
}

void ColorTest1()
{
	uint8_t color = 0;
	uint32_t line; 

	for(int i=0 ; i<4 ; i++)
	{
		
		for(int j=0;j<451/4;j++)
		{
			for(int l=0;l<4;l++)
			{
			for(int k=0; k<68 ; k++)
			{
		
				
							//if(i<3)
							//{
							//	color = l << i*2; 
							//}
							//else
							//{
								color = l;	
						//	}

							display_buf[l*68 + k] = LCD_color(color);
						
				}
			}

		
		line = j + i*(451/4);


	
		send_pixels_finish();
		send_pixels_start(line);

		line_buf = (line_buf == line_buf_a) ? line_buf_b : line_buf_a;
		}
	}
}


static void send_pixels_start(int ln)
{
	// Packed pixel format: xxRGBrgb
	// Then needs to be split into two planes to update the lines

	line_buf[0] = 0b10000000;             // Update mode, 64 color mode
	line_buf[0] |= ((ln + 512) >> 8) & 3; // Higher 2 bits
	line_buf[1] = ln & 0xff;              // Rest of address

	// Pack the pixels for this line (LOW PLANE)
	int ppo = 2;
	for (int upo = 0; upo < 272; upo += 8) {
		int po          = upo;
		line_buf[ppo++] = ((display_buf[po] << 5) & 0b11100000) |
		                  ((display_buf[po + 1] << 2) & 0b00011100) |
		                  ((display_buf[po + 2] >> 1) & 0b00000011);
		line_buf[ppo++] =
		    ((display_buf[po + 2] << 7) & 0b10000000) | ((display_buf[po + 3] << 4) & 0b01110000) |
		    ((display_buf[po + 4] << 1) & 0b00001110) | ((display_buf[po + 5] >> 2) & 0b00000001);
		line_buf[ppo++] = ((display_buf[po + 5] << 6) & 0b11000000) |
		                  ((display_buf[po + 6] << 3) & 0b00111000) |
		                  ((display_buf[po + 7]) & 0b00000111);
	}
	line_buf[ppo] = 0b00000000;         // Dummy data
	line_buf[ppo++] |= ((ln) >> 8) & 3; // Higher 2 bits THIS IS THE LOW PLANE
	line_buf[ppo++] = ln & 0xff;        // Rest of address

	// Pack the pixels for this line (HIGH PLANE)
	for (int upo = 0; upo < 272; upo += 8) {
		int po          = upo;
		line_buf[ppo++] = ((display_buf[po] << 2) & 0b11100000) |
		                  ((display_buf[po + 1] >> 1) & 0b00011100) |
		                  ((display_buf[po + 2] >> 4) & 0b00000011);
		line_buf[ppo++] =
		    ((display_buf[po + 2] << 4) & 0b10000000) | ((display_buf[po + 3] << 1) & 0b01110000) |
		    ((display_buf[po + 4] >> 2) & 0b00001110) | ((display_buf[po + 5] >> 5) & 0b00000001);
		line_buf[ppo++] = ((display_buf[po + 5] << 3) & 0b11000000) |
		                  ((display_buf[po + 6]) & 0b00111000) |
		                  ((display_buf[po + 7] >> 3) & 0b00000111);
	}
	gpio_put(MEMLCD_CS_PIN, 1);

	// spi_write_blocking(MEMLCD_SPI_ID, line_buf, 210); // TODO: Use DMA
	dma_channel_configure(dma_tx, &dma_conf, &spi_get_hw(MEMLCD_SPI)->dr, line_buf, 210, false);
	dma_start_channel_mask(1u << dma_tx);

	// gpio_put(MEMLCD_CS_PIN, 0);
}
static void send_pixels_finish()
{
	dma_channel_wait_for_finish_blocking(dma_tx);
	sleep_us(50); // ¯\_(ツ)_/¯
	gpio_put(MEMLCD_CS_PIN, 0);
}



int main() 
{

	stdio_init_all();
	LCD_init();

    const uint LED_PIN = 8;
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 1);

	int l = 0;
	//Top();
	//Bottom();
	LCD_fill();
	sleep_ms(1000);
    while (true)
    {
		LCD_update_landscape();
   		 //ColorTest1();
		//printf("Hello, world!\n");
		//clear();

	   //sleep_ms(12);
	   // LCD_update();
	    //LCD_update_landscape();
    }
}
