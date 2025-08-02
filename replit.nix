{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.aiogram
    pkgs.python310Packages.python-dotenv
    pkgs.opencv4
    pkgs.zbar
    pkgs.tesseract
    pkgs.pillow
    pkgs.libGL
  ];
}