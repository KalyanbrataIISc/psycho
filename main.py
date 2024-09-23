from experiment import UserDataWindow
import sys
import subprocess
from PyQt5.QtWidgets import QApplication

# Reinstall necessary packages
required_packages = ['PyQt5', 'numpy', 'pandas', 'sounddevice']

for package in required_packages:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package])
print("Packages installed successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize and show the user data collection window
    user_data_window = UserDataWindow()
    user_data_window.show()

    sys.exit(app.exec_())