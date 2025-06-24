{
  description = "eBay Sold Listings Scraper API";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python311;
        pythonPackages = python.pkgs;
      in
      {
        packages.ebay-scraper-api = pythonPackages.buildPythonApplication {
          pname = "ebay-scraper-api";
          version = "0.2.0";
          src = ./.;
          entryPoints = { "ebay-api" = "api:app"; }; # Not used by uvicorn, but good for completeness
          propagatedBuildInputs = with pythonPackages; [
            fastapi
            uvicorn
            requests
            beautifulsoup4
            numpy
            pandas
          ];
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pythonPackages; [
            fastapi
            uvicorn
            requests
            beautifulsoup4
            numpy
            pandas
          ];
          shellHook = ''
            echo "🔧 Dev shell for ebay-scraper! Use 'uvicorn api:app --reload --port 8080' to start the server."
          '';
        };
      }
    );
}