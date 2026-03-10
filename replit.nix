{pkgs}: {
  deps = [
    pkgs.postgresql13Packages.tds_fdw
  ];
}
