{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/24.05";
    rand-nix = {
      url = "github:figsoda/rand-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    rand-nix,
  }: let
    lib = nixpkgs.lib;
  in {
    ffi = import ./ffi.nix {inherit lib rand-nix;};
  };
}
