{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.aiogram
    pkgs.python311Packages.python-dotenv
    pkgs.opencv4
    pkgs.zbar
    pkgs.tesseract
    pkgs.pillow
    pkgs.libGL
  ];
}