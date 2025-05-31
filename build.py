import PyInstaller.__main__
import os
import shutil

def build_executable():
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Check if we're building the web version or Tkinter version
    if os.path.exists('app.py'):
        main_file = 'app.py'
        app_name = 'CalculadoraNegociacao_Web'
        # PyInstaller arguments for web version
        args = [
            main_file,
            '--onefile',
            '--windowed',
            f'--name={app_name}',
            '--add-data=index.html;.',
            '--add-data=app.js;.',
            '--clean',
            '--noconfirm'
        ]
    else:
        # Build Tkinter version
        main_file = 'cal_negoc.py'
        app_name = 'CalculadoraNegociacao_Tkinter'
        # PyInstaller arguments for Tkinter version
        args = [
            main_file,
            '--onefile',
            '--windowed',
            f'--name={app_name}',
            '--clean',
            '--noconfirm'
        ]
    
    # Add icon if it exists
    if os.path.exists('icon.ico'):
        args.extend(['--icon=icon.ico'])
    
    print(f"Building {main_file} as {app_name}...")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print(f"Build completed! Check the 'dist' folder for {app_name}.exe")

if __name__ == "__main__":
    build_executable()
