-- ==========================================
-- Location Hierarchy Lookup Table
-- Enables automated, consistent location data import from real estate APIs
-- ==========================================

-- 1) Create location_hierarchy lookup table
CREATE TABLE IF NOT EXISTS location_hierarchy (
    id SERIAL PRIMARY KEY,
    area_neighborhood VARCHAR(100) NOT NULL,        -- The area/neighborhood/village name
    judet VARCHAR(50) NOT NULL,                     -- County: 'București' or 'Ilfov'
    city_town VARCHAR(100) NOT NULL,                -- City/Town for Ilfov, or 'București' for sectors
    sector INTEGER,                                 -- 1-6 for București sectors, NULL for Ilfov
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(area_neighborhood, judet, sector)       -- Prevent duplicates
);

-- 2) Create indexes for fast lookups
CREATE INDEX idx_location_area ON location_hierarchy(area_neighborhood);
CREATE INDEX idx_location_judet_sector ON location_hierarchy(judet, sector);
CREATE INDEX idx_location_city_town ON location_hierarchy(city_town);
CREATE INDEX idx_location_lookup ON location_hierarchy(area_neighborhood, judet) WHERE sector IS NOT NULL;

-- ==========================================
-- BUCHAREST: Sector 1 (23 neighborhoods)
-- ==========================================
INSERT INTO location_hierarchy (area_neighborhood, judet, city_town, sector) VALUES
('Aviatorilor', 'București', 'București', 1),
('Aviației', 'București', 'București', 1),
('Băneasa', 'București', 'București', 1),
('Bucureștii Noi', 'București', 'București', 1),
('Chibrit', 'București', 'București', 1),
('Dămăroaia', 'București', 'București', 1),
('Domenii', 'București', 'București', 1),
('Dorobanți', 'București', 'București', 1),
('Floreasca (North)', 'București', 'București', 1),
('Gara de Nord', 'București', 'București', 1),
('Grivița', 'București', 'București', 1),
('Pajura', 'București', 'București', 1),
('Pipera (Bucharest)', 'București', 'București', 1),
('Piața Romană', 'București', 'București', 1),
('Piața Victoriei', 'București', 'București', 1),
('Primăverii', 'București', 'București', 1),
('Sisești', 'București', 'București', 1),
('Străulești', 'București', 'București', 1),
('Cotroceni', 'București', 'București', 1),
('Dorobanți (North)', 'București', 'București', 1),
('Aviatorilor (South)', 'București', 'București', 1),
('Pipera (Central)', 'București', 'București', 1),
('Gara de Nord (East)', 'București', 'București', 1);

-- ==========================================
-- BUCHAREST: Sector 2 (23 neighborhoods)
-- ==========================================
INSERT INTO location_hierarchy (area_neighborhood, judet, city_town, sector) VALUES
('Andronache', 'București', 'București', 2),
('Baicului', 'București', 'București', 2),
('Colentina', 'București', 'București', 2),
('Floreasca (Main)', 'București', 'București', 2),
('Fundeni', 'București', 'București', 2),
('Gara Obor', 'București', 'București', 2),
('Iancului', 'București', 'București', 2),
('Moșior', 'București', 'București', 2),
('Obor', 'București', 'București', 2),
('Pantelimon', 'București', 'București', 2),
('Petricani', 'București', 'București', 2),
('Pipera (South)', 'București', 'București', 2),
('Ștefan cel Mare', 'București', 'București', 2),
('Tei', 'București', 'București', 2),
('Teiul Doamnei', 'București', 'București', 2),
('Vatra Luminoasă', 'București', 'București', 2),
('Obor (North)', 'București', 'București', 2),
('Colentina (East)', 'București', 'București', 2),
('Tei (North)', 'București', 'București', 2),
('Fundeni (South)', 'București', 'București', 2),
('Floreasca (East)', 'București', 'București', 2),
('Moșior (East)', 'București', 'București', 2),
('Iancului (South)', 'București', 'București', 2);

-- ==========================================
-- BUCHAREST: Sector 3 (23 neighborhoods)
-- ==========================================
INSERT INTO location_hierarchy (area_neighborhood, judet, city_town, sector) VALUES
('23 August', 'București', 'București', 3),
('Balta Albă', 'București', 'București', 3),
('Centrul Civic', 'București', 'București', 3),
('Centrul Vechi (Lipscani)', 'București', 'București', 3),
('Dristor', 'București', 'București', 3),
('Dudești', 'București', 'București', 3),
('Muncii', 'București', 'București', 3),
('Pallady', 'București', 'București', 3),
('Piața Unirii (East)', 'București', 'București', 3),
('Sălăjan', 'București', 'București', 3),
('Titan', 'București', 'București', 3),
('Universitate', 'București', 'București', 3),
('Vitan', 'București', 'București', 3),
('Dristor (North)', 'București', 'București', 3),
('Dudești (South)', 'București', 'București', 3),
('Titan (West)', 'București', 'București', 3),
('Piața Unirii (Central)', 'București', 'București', 3),
('Muncii (North)', 'București', 'București', 3),
('Obor (South)', 'București', 'București', 3),
('Dristor (East)', 'București', 'București', 3),
('Titan (South)', 'București', 'București', 3),
('Vitan (West)', 'București', 'București', 3),
('Pallady (North)', 'București', 'București', 3);

-- ==========================================
-- BUCHAREST: Sector 4 (23 neighborhoods)
-- ==========================================
INSERT INTO location_hierarchy (area_neighborhood, judet, city_town, sector) VALUES
('Apărătorii Patriei', 'București', 'București', 4),
('Berceni', 'București', 'București', 4),
('Brâncoveanu', 'București', 'București', 4),
('Eroii Revoluției', 'București', 'București', 4),
('Giurgiului', 'București', 'București', 4),
('Metalurgiei', 'București', 'București', 4),
('Olteniței', 'București', 'București', 4),
('Piața Unirii (South)', 'București', 'București', 4),
('Progresul', 'București', 'București', 4),
('Timpuri Noi', 'București', 'București', 4),
('Tineretului', 'București', 'București', 4),
('Văcărești', 'București', 'București', 4),
('Brâncoveanu (East)', 'București', 'București', 4),
('Olteniței (North)', 'București', 'București', 4),
('Metalurgiei (East)', 'București', 'București', 4),
('Tineretului (West)', 'București', 'București', 4),
('Apărătorii Patriei (North)', 'București', 'București', 4),
('Eroii Revoluției (South)', 'București', 'București', 4),
('Progresul (North)', 'București', 'București', 4),
('Văcărești (East)', 'București', 'București', 4),
('Timpuri Noi (West)', 'București', 'București', 4),
('Giurgiului (South)', 'București', 'București', 4),
('Berceni (North)', 'București', 'București', 4);

-- ==========================================
-- BUCHAREST: Sector 5 (24 neighborhoods)
-- ==========================================
INSERT INTO location_hierarchy (area_neighborhood, judet, city_town, sector) VALUES
('13 Septembrie', 'București', 'București', 5),
('Antiaeriană', 'București', 'București', 5),
('Cotroceni', 'București', 'București', 5),
('Ferentari', 'București', 'București', 5),
('Ghencea (South)', 'București', 'București', 5),
('Giurgiului (West)', 'București', 'București', 5),
('Mărgeanului', 'București', 'București', 5),
('Panduri', 'București', 'București', 5),
('Piața Unirii (SW/Parliament)', 'București', 'București', 5),
('Rahova', 'București', 'București', 5),
('Sălaj', 'București', 'București', 5),
('Sebastian', 'București', 'București', 5),
('Antiaeriană (East)', 'București', 'București', 5),
('Ferentari (North)', 'București', 'București', 5),
('Cotroceni (East)', 'București', 'București', 5),
('Ghencea (Central)', 'București', 'București', 5),
('Panduri (North)', 'București', 'București', 5),
('Rahova (South)', 'București', 'București', 5),
('Sălaj (West)', 'București', 'București', 5),
('13 Septembrie (East)', 'București', 'București', 5),
('Mărgeanului (North)', 'București', 'București', 5),
('Giurgiului (Central)', 'București', 'București', 5),
('Sebastian (East)', 'București', 'București', 5),
('Antiaeriană (North)', 'București', 'București', 5);

-- ==========================================
-- BUCHAREST: Sector 6 (24 neighborhoods)
-- ==========================================
INSERT INTO location_hierarchy (area_neighborhood, judet, city_town, sector) VALUES
('Crângași', 'București', 'București', 6),
('Drumul Taberei', 'București', 'București', 6),
('Ghencea (North)', 'București', 'București', 6),
('Giulești', 'București', 'București', 6),
('Grozăvești', 'București', 'București', 6),
('Militari', 'București', 'București', 6),
('Pace', 'București', 'București', 6),
('Regie', 'București', 'București', 6),
('Uverturii', 'București', 'București', 6),
('Virtuții', 'București', 'București', 6),
('Drumul Taberei (West)', 'București', 'București', 6),
('Militari (East)', 'București', 'București', 6),
('Giulești (South)', 'București', 'București', 6),
('Grozăvești (North)', 'București', 'București', 6),
('Crângași (South)', 'București', 'București', 6),
('Pace (East)', 'București', 'București', 6),
('Regie (North)', 'București', 'București', 6),
('Virtuții (West)', 'București', 'București', 6),
('Uverturii (East)', 'București', 'București', 6),
('Ghencea (West)', 'București', 'București', 6),
('Militari (North)', 'București', 'București', 6),
('Drumul Taberei (East)', 'București', 'București', 6),
('Giulești (North)', 'București', 'București', 6),
('Grozăvești (East)', 'București', 'București', 6);

-- ==========================================
-- ILFOV: Towns (40 neighborhoods)
-- ==========================================
INSERT INTO location_hierarchy (area_neighborhood, judet, city_town, sector) VALUES
('Bragadiru', 'Ilfov', 'Bragadiru', NULL),
('Buftea', 'Ilfov', 'Buftea', NULL),
('Buciumeni', 'Ilfov', 'Buftea', NULL),
('Chitila', 'Ilfov', 'Chitila', NULL),
('Rudeni', 'Ilfov', 'Chitila', NULL),
('Măgurele', 'Ilfov', 'Măgurele', NULL),
('Alunișu', 'Ilfov', 'Măgurele', NULL),
('Dumitrana', 'Ilfov', 'Măgurele', NULL),
('Pruni', 'Ilfov', 'Măgurele', NULL),
('Vârteju', 'Ilfov', 'Măgurele', NULL),
('Otopeni', 'Ilfov', 'Otopeni', NULL),
('Odăile', 'Ilfov', 'Otopeni', NULL),
('Pantelimon (Town)', 'Ilfov', 'Pantelimon', NULL),
('Popești-Leordeni', 'Ilfov', 'Popești-Leordeni', NULL),
('Voluntari', 'Ilfov', 'Voluntari', NULL),
('Pipera (Voluntari)', 'Ilfov', 'Voluntari', NULL);

-- ==========================================
-- ILFOV: Communes (32 locations)
-- ==========================================
INSERT INTO location_hierarchy (area_neighborhood, judet, city_town, sector) VALUES
('1 Decembrie', 'Ilfov', '1 Decembrie', NULL),
('Afumați', 'Ilfov', 'Afumați', NULL),
('Balotești', 'Ilfov', 'Balotești', NULL),
('Berceni (Commune)', 'Ilfov', 'Berceni (Commune)', NULL),
('Brănești', 'Ilfov', 'Brănești', NULL),
('Cernica', 'Ilfov', 'Cernica', NULL),
('Chiajna', 'Ilfov', 'Chiajna', NULL),
('Ciolpani', 'Ilfov', 'Ciolpani', NULL),
('Ciorogârla', 'Ilfov', 'Ciorogârla', NULL),
('Clinceni', 'Ilfov', 'Clinceni', NULL),
('Copăceni', 'Ilfov', 'Copăceni', NULL),
('Corbeanca', 'Ilfov', 'Corbeanca', NULL),
('Cornetu', 'Ilfov', 'Cornetu', NULL),
('Dărăști-Ilfov', 'Ilfov', 'Dărăști-Ilfov', NULL),
('Dascălu', 'Ilfov', 'Dascălu', NULL),
('Dobroești', 'Ilfov', 'Dobroești', NULL),
('Domnești', 'Ilfov', 'Domnești', NULL),
('Dragomirești-Vale', 'Ilfov', 'Dragomirești-Vale', NULL),
('Găneasa', 'Ilfov', 'Găneasa', NULL),
('Glina', 'Ilfov', 'Glina', NULL),
('Grădiștea', 'Ilfov', 'Grădiștea', NULL),
('Gruiu', 'Ilfov', 'Gruiu', NULL),
('Jilava', 'Ilfov', 'Jilava', NULL),
('Moara Vlăsiei', 'Ilfov', 'Moara Vlăsiei', NULL),
('Mogoșoaia', 'Ilfov', 'Mogoșoaia', NULL),
('Nuci', 'Ilfov', 'Nuci', NULL),
('Periș', 'Ilfov', 'Periș', NULL),
('Petrăchioaia', 'Ilfov', 'Petrăchioaia', NULL),
('Snagov', 'Ilfov', 'Snagov', NULL),
('Ștefăneștii de Jos', 'Ilfov', 'Ștefăneștii de Jos', NULL),
('Tunari', 'Ilfov', 'Tunari', NULL),
('Vidra', 'Ilfov', 'Vidra', NULL);

-- ==========================================
-- VERIFICATION QUERIES
-- ==========================================

-- Count total locations
-- SELECT COUNT(*) as total_locations FROM location_hierarchy;
-- Expected: ~172 unique locations (140 Bucharest + 32 Ilfov)

-- Count by judet
-- SELECT judet, COUNT(*) FROM location_hierarchy GROUP BY judet;
-- Expected: București: 140, Ilfov: ~32

-- Lookup example
-- SELECT * FROM location_hierarchy WHERE area_neighborhood ILIKE '%Pipera%';
-- Expected: Multiple results (Pipera in different sectors/towns)

-- ==========================================
-- ✅ Location Hierarchy Lookup Table Complete
-- Used by: API import scripts, data validation, consistent location mapping
-- ==========================================
