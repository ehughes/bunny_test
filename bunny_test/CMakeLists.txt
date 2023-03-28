add_executable(bunny_test
               blink.c
               top.c
               bottom.c
               frame.c
                )

add_executable(bunny_test_no_ai
                blink.c
                top.c
                bottom.c
                frame_no_ai.c
                )
 
add_executable(bunny_test_box_only
                blink.c
                top.c
                bottom.c
                frame_box_only.c
                )
 
# pull in common dependencies
target_link_libraries(bunny_test pico_stdlib hardware_pwm hardware_spi hardware_dma)
target_link_libraries(bunny_test_no_ai pico_stdlib hardware_pwm hardware_spi hardware_dma)
target_link_libraries(bunny_test_box_only pico_stdlib hardware_pwm hardware_spi hardware_dma)

# create map/bin/hex file etc.
pico_add_extra_outputs(bunny_test)
pico_add_extra_outputs(bunny_test_no_ai)
pico_add_extra_outputs(bunny_test_box_only)

