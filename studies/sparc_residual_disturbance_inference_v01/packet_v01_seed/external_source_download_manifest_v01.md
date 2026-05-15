# External Source Download Manifest v0.1

This packet records structured local downloads for the external-validation expansion. Raw downloaded files are stored under `data/raw/` and are intentionally excluded from git. The public packet contains only derived manifests and indexes.

## Download Summary

- Sources attempted: 7
- Sources downloaded: 5
- Sources failed: 2
- HALOGAS indexed files: 192
- HALOGAS files matching candidate SPARC overlap names: 40

## Next Step

Use the local source files to build alias crossmatch tables before downloading large raw cubes. Large FITS products should remain local unless a specific derived summary requires them.

## Generated Files

- `external_source_download_manifest_v01.csv`
- `halogas_zenodo_file_index_v01.csv`

## Guardrail

`raw_downloads_local_only_public_packet_derived_index_only`
