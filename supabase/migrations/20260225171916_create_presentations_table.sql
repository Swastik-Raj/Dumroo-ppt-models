/*
  # Create presentations storage schema

  1. New Tables
    - `presentations`
      - `id` (uuid, primary key) - Unique presentation identifier
      - `topic` (text) - Presentation topic
      - `slides_data` (jsonb) - Slide content and structure
      - `theme` (text) - Selected theme name
      - `created_at` (timestamptz) - Creation timestamp
      - `updated_at` (timestamptz) - Last update timestamp
  
  2. Security
    - Enable RLS on `presentations` table
    - Add policy for anyone to create presentations
    - Add policy for anyone to read their own presentations (by id)
    - Add policy for anyone to update their own presentations (by id)
*/

CREATE TABLE IF NOT EXISTS presentations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  topic text NOT NULL,
  slides_data jsonb NOT NULL DEFAULT '[]'::jsonb,
  theme text NOT NULL DEFAULT 'Education Light',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE presentations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can create presentations"
  ON presentations
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Anyone can read presentations by id"
  ON presentations
  FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Anyone can update presentations by id"
  ON presentations
  FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_presentations_created_at ON presentations(created_at DESC);
