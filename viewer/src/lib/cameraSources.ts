// cameraSources.ts
// Public real space/spacecraft imagery sources for the Dragon Lady Observatory
// Preserved as LAB / CANDIDATE file only.
// Prior ground/all-sky candidates were rejected because they looked like
// fisheye/ground-level trees instead of space.
// Goldwing disabled tabs on /telescope until Tanya manually vets + provides good sky/space sources.
// The full wiring (tabs, panel, image+video support, per-source refresh, localStorage, prominent view, dim) is kept intact for when good feeds arrive.
// Do not re-enable the selector or auto-open any camera until explicitly told the sources are good.

export type CameraSource =
  | {
      kind: "latest-video";
      id: string;
      name: string;
      videoUrl: string;
      posterUrl?: string;
      pageUrl?: string;
      refreshSeconds: number;
      credit: string;
    }
  | {
      kind: "latest-image";
      id: string;
      name: string;
      imageUrl: string;
      pageUrl?: string;
      refreshSeconds: number;
      credit: string;
    }
  | {
      kind: "html-discovery";
      id?: string;
      name: string;
      pageUrl: string;
      selectorHint?: string;
      refreshSeconds?: number;
      credit: string;
    }
  | {
      kind: "json-api";
      id?: string;
      name: string;
      endpoint: string;
      refreshSeconds: number;
      credit: string;
    };

export const cameraSources: CameraSource[] = [
  {
    kind: "latest-image",
    id: "sdo-sun-171",
    name: "SDO Sun 171 Å",
    imageUrl: "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0171.jpg",
    pageUrl: "https://sdo.gsfc.nasa.gov/data/bestpractice.php",
    refreshSeconds: 900,
    credit: "NASA Solar Dynamics Observatory — near-real-time AIA 171 Å solar image",
  },
  {
    kind: "latest-image",
    id: "sdo-sun-304",
    name: "SDO Sun 304 Å",
    imageUrl: "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0304.jpg",
    pageUrl: "https://sdo.gsfc.nasa.gov/data/bestpractice.php",
    refreshSeconds: 900,
    credit: "NASA Solar Dynamics Observatory — near-real-time AIA 304 Å solar image",
  },
  {
    kind: "latest-image",
    id: "goes-east-full-disk",
    name: "GOES East Full Disk",
    imageUrl: "https://cdn.star.nesdis.noaa.gov/GOES19/ABI/FD/GEOCOLOR/latest.jpg",
    pageUrl: "https://www.star.nesdis.noaa.gov/GOES/index.php",
    refreshSeconds: 600,
    credit: "NOAA/NESDIS/STAR GOES East — GeoColor full-disk Earth image",
  },
  {
    kind: "latest-image",
    id: "goes-west-full-disk",
    name: "GOES West Full Disk",
    imageUrl: "https://cdn.star.nesdis.noaa.gov/GOES18/ABI/FD/GEOCOLOR/latest.jpg",
    pageUrl: "https://www.star.nesdis.noaa.gov/GOES/index.php",
    refreshSeconds: 600,
    credit: "NOAA/NESDIS/STAR GOES West — GeoColor full-disk Earth image",
  },
  {
    kind: "json-api",
    id: "dscovr-epic-natural",
    name: "DSCOVR EPIC Earth",
    endpoint: "https://api.nasa.gov/EPIC/api/natural?api_key=DEMO_KEY",
    refreshSeconds: 3600,
    credit: "NASA/NOAA DSCOVR EPIC — Earth from L1; build image URL from API metadata",
  },
];
