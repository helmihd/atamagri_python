import pygame

# Inisialisasi pygame dan joystick
pygame.init()

# Cek jumlah joystick yang terhubung
joystick_count = pygame.joystick.get_count()
print(f"Jumlah joystick yang terhubung: {joystick_count}")

if joystick_count > 0:
    # Pilih joystick pertama
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # Program utama
    try:
        while True:
            pygame.event.pump()  # Memperbarui status joystick

            # Cek status tombol
            for button in range(joystick.get_numbuttons()):
                if joystick.get_button(button):  # Jika tombol ditekan
                    print(f"Tombol {button} ditekan")
                    
            pygame.time.wait(100)  # Tunggu sebentar untuk menghindari penggunaan CPU yang berlebihan

    except KeyboardInterrupt:
        print("Program dihentikan")
    finally:
        pygame.quit()  # Tutup pygame saat program selesai
