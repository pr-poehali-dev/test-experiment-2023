export interface Member {
  id: number;
  name: string;
  role: string | null;
  joined_year: number | null;
  location: string | null;
  favorite_fish: string | null;
  trips_count: number;
  created_at: string | null;
}

export interface Spot {
  id: number;
  name: string;
  region: string | null;
  fish_types: string | null;
  difficulty: string | null;
  created_at: string | null;
}

export interface Trip {
  id: number;
  title: string;
  spot_id: number | null;
  date: string;
  participants_count: number;
  organizer: string | null;
  status: string;
  created_at: string | null;
}
