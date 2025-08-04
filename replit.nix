{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.opencv4
    pkgs.zbar
    pkgs.tesseract
    pkgs.libGL
    pkgs.numpy
  ];
}