/*
====================================================================
fares.pl — Auto-generated from electric_train_fares.csv.

DO NOT EDIT BY HAND. Regenerate with `python scripts/build_fares.py`.

One `fare(Agency, Origin, Destination, PriceTHB).` fact per
(agency, station-pair) whose endpoints are both modelled in
knowledge_base.pl. Non-modelled stations/agencies are dropped
at ingest; see scripts/build_fares.py for the mapping.

Source rows read:      7394
Facts emitted:         644
Dropped (agency):      1553
Dropped (stop):        5162
Dropped (self-pair):   35
====================================================================
*/

:- discontiguous fare/4.

% --- bem (132 fares) ---
fare(bem, 'Hua Lamphong (BL28)', 'Khlong Toei (BL24)', 25).
fare(bem, 'Hua Lamphong (BL28)', 'Lumphini (BL25)', 22).
fare(bem, 'Hua Lamphong (BL28)', 'Phetchaburi (BL21)', 32).
fare(bem, 'Hua Lamphong (BL28)', 'Phra Ram 9 (BL20)', 35).
fare(bem, 'Hua Lamphong (BL28)', 'Queen Sirikit (BL23)', 27).
fare(bem, 'Hua Lamphong (BL28)', 'Sam Yan (BL27)', 17).
fare(bem, 'Hua Lamphong (BL28)', 'Sam Yot (BL30)', 20).
fare(bem, 'Hua Lamphong (BL28)', 'Sanam Chai (BL31)', 22).
fare(bem, 'Hua Lamphong (BL28)', 'Silom (BL26)', 20).
fare(bem, 'Hua Lamphong (BL28)', 'Sukhumvit (BL22)', 30).
fare(bem, 'Hua Lamphong (BL28)', 'Wat Mangkon (BL29)', 17).
fare(bem, 'Khlong Toei (BL24)', 'Hua Lamphong (BL28)', 25).
fare(bem, 'Khlong Toei (BL24)', 'Lumphini (BL25)', 17).
fare(bem, 'Khlong Toei (BL24)', 'Phetchaburi (BL21)', 22).
fare(bem, 'Khlong Toei (BL24)', 'Phra Ram 9 (BL20)', 25).
fare(bem, 'Khlong Toei (BL24)', 'Queen Sirikit (BL23)', 17).
fare(bem, 'Khlong Toei (BL24)', 'Sam Yan (BL27)', 22).
fare(bem, 'Khlong Toei (BL24)', 'Sam Yot (BL30)', 30).
fare(bem, 'Khlong Toei (BL24)', 'Sanam Chai (BL31)', 32).
fare(bem, 'Khlong Toei (BL24)', 'Silom (BL26)', 20).
fare(bem, 'Khlong Toei (BL24)', 'Sukhumvit (BL22)', 20).
fare(bem, 'Khlong Toei (BL24)', 'Wat Mangkon (BL29)', 27).
fare(bem, 'Lumphini (BL25)', 'Hua Lamphong (BL28)', 22).
fare(bem, 'Lumphini (BL25)', 'Khlong Toei (BL24)', 17).
fare(bem, 'Lumphini (BL25)', 'Phetchaburi (BL21)', 25).
fare(bem, 'Lumphini (BL25)', 'Phra Ram 9 (BL20)', 27).
fare(bem, 'Lumphini (BL25)', 'Queen Sirikit (BL23)', 20).
fare(bem, 'Lumphini (BL25)', 'Sam Yan (BL27)', 20).
fare(bem, 'Lumphini (BL25)', 'Sam Yot (BL30)', 27).
fare(bem, 'Lumphini (BL25)', 'Sanam Chai (BL31)', 30).
fare(bem, 'Lumphini (BL25)', 'Silom (BL26)', 17).
fare(bem, 'Lumphini (BL25)', 'Sukhumvit (BL22)', 22).
fare(bem, 'Lumphini (BL25)', 'Wat Mangkon (BL29)', 25).
fare(bem, 'Phetchaburi (BL21)', 'Hua Lamphong (BL28)', 32).
fare(bem, 'Phetchaburi (BL21)', 'Khlong Toei (BL24)', 22).
fare(bem, 'Phetchaburi (BL21)', 'Lumphini (BL25)', 25).
fare(bem, 'Phetchaburi (BL21)', 'Phra Ram 9 (BL20)', 17).
fare(bem, 'Phetchaburi (BL21)', 'Queen Sirikit (BL23)', 20).
fare(bem, 'Phetchaburi (BL21)', 'Sam Yan (BL27)', 30).
fare(bem, 'Phetchaburi (BL21)', 'Sam Yot (BL30)', 37).
fare(bem, 'Phetchaburi (BL21)', 'Sanam Chai (BL31)', 40).
fare(bem, 'Phetchaburi (BL21)', 'Silom (BL26)', 27).
fare(bem, 'Phetchaburi (BL21)', 'Sukhumvit (BL22)', 17).
fare(bem, 'Phetchaburi (BL21)', 'Wat Mangkon (BL29)', 35).
fare(bem, 'Phra Ram 9 (BL20)', 'Hua Lamphong (BL28)', 35).
fare(bem, 'Phra Ram 9 (BL20)', 'Khlong Toei (BL24)', 25).
fare(bem, 'Phra Ram 9 (BL20)', 'Lumphini (BL25)', 27).
fare(bem, 'Phra Ram 9 (BL20)', 'Phetchaburi (BL21)', 17).
fare(bem, 'Phra Ram 9 (BL20)', 'Queen Sirikit (BL23)', 22).
fare(bem, 'Phra Ram 9 (BL20)', 'Sam Yan (BL27)', 32).
fare(bem, 'Phra Ram 9 (BL20)', 'Sam Yot (BL30)', 40).
fare(bem, 'Phra Ram 9 (BL20)', 'Sanam Chai (BL31)', 42).
fare(bem, 'Phra Ram 9 (BL20)', 'Silom (BL26)', 30).
fare(bem, 'Phra Ram 9 (BL20)', 'Sukhumvit (BL22)', 20).
fare(bem, 'Phra Ram 9 (BL20)', 'Wat Mangkon (BL29)', 37).
fare(bem, 'Queen Sirikit (BL23)', 'Hua Lamphong (BL28)', 27).
fare(bem, 'Queen Sirikit (BL23)', 'Khlong Toei (BL24)', 17).
fare(bem, 'Queen Sirikit (BL23)', 'Lumphini (BL25)', 20).
fare(bem, 'Queen Sirikit (BL23)', 'Phetchaburi (BL21)', 20).
fare(bem, 'Queen Sirikit (BL23)', 'Phra Ram 9 (BL20)', 22).
fare(bem, 'Queen Sirikit (BL23)', 'Sam Yan (BL27)', 25).
fare(bem, 'Queen Sirikit (BL23)', 'Sam Yot (BL30)', 32).
fare(bem, 'Queen Sirikit (BL23)', 'Sanam Chai (BL31)', 35).
fare(bem, 'Queen Sirikit (BL23)', 'Silom (BL26)', 22).
fare(bem, 'Queen Sirikit (BL23)', 'Sukhumvit (BL22)', 17).
fare(bem, 'Queen Sirikit (BL23)', 'Wat Mangkon (BL29)', 30).
fare(bem, 'Sam Yan (BL27)', 'Hua Lamphong (BL28)', 17).
fare(bem, 'Sam Yan (BL27)', 'Khlong Toei (BL24)', 22).
fare(bem, 'Sam Yan (BL27)', 'Lumphini (BL25)', 20).
fare(bem, 'Sam Yan (BL27)', 'Phetchaburi (BL21)', 30).
fare(bem, 'Sam Yan (BL27)', 'Phra Ram 9 (BL20)', 32).
fare(bem, 'Sam Yan (BL27)', 'Queen Sirikit (BL23)', 25).
fare(bem, 'Sam Yan (BL27)', 'Sam Yot (BL30)', 22).
fare(bem, 'Sam Yan (BL27)', 'Sanam Chai (BL31)', 25).
fare(bem, 'Sam Yan (BL27)', 'Silom (BL26)', 17).
fare(bem, 'Sam Yan (BL27)', 'Sukhumvit (BL22)', 27).
fare(bem, 'Sam Yan (BL27)', 'Wat Mangkon (BL29)', 20).
fare(bem, 'Sam Yot (BL30)', 'Hua Lamphong (BL28)', 20).
fare(bem, 'Sam Yot (BL30)', 'Khlong Toei (BL24)', 30).
fare(bem, 'Sam Yot (BL30)', 'Lumphini (BL25)', 27).
fare(bem, 'Sam Yot (BL30)', 'Phetchaburi (BL21)', 37).
fare(bem, 'Sam Yot (BL30)', 'Phra Ram 9 (BL20)', 40).
fare(bem, 'Sam Yot (BL30)', 'Queen Sirikit (BL23)', 32).
fare(bem, 'Sam Yot (BL30)', 'Sam Yan (BL27)', 22).
fare(bem, 'Sam Yot (BL30)', 'Sanam Chai (BL31)', 17).
fare(bem, 'Sam Yot (BL30)', 'Silom (BL26)', 25).
fare(bem, 'Sam Yot (BL30)', 'Sukhumvit (BL22)', 35).
fare(bem, 'Sam Yot (BL30)', 'Wat Mangkon (BL29)', 17).
fare(bem, 'Sanam Chai (BL31)', 'Hua Lamphong (BL28)', 22).
fare(bem, 'Sanam Chai (BL31)', 'Khlong Toei (BL24)', 32).
fare(bem, 'Sanam Chai (BL31)', 'Lumphini (BL25)', 30).
fare(bem, 'Sanam Chai (BL31)', 'Phetchaburi (BL21)', 40).
fare(bem, 'Sanam Chai (BL31)', 'Phra Ram 9 (BL20)', 42).
fare(bem, 'Sanam Chai (BL31)', 'Queen Sirikit (BL23)', 35).
fare(bem, 'Sanam Chai (BL31)', 'Sam Yan (BL27)', 25).
fare(bem, 'Sanam Chai (BL31)', 'Sam Yot (BL30)', 17).
fare(bem, 'Sanam Chai (BL31)', 'Silom (BL26)', 27).
fare(bem, 'Sanam Chai (BL31)', 'Sukhumvit (BL22)', 37).
fare(bem, 'Sanam Chai (BL31)', 'Wat Mangkon (BL29)', 20).
fare(bem, 'Silom (BL26)', 'Hua Lamphong (BL28)', 20).
fare(bem, 'Silom (BL26)', 'Khlong Toei (BL24)', 20).
fare(bem, 'Silom (BL26)', 'Lumphini (BL25)', 17).
fare(bem, 'Silom (BL26)', 'Phetchaburi (BL21)', 27).
fare(bem, 'Silom (BL26)', 'Phra Ram 9 (BL20)', 30).
fare(bem, 'Silom (BL26)', 'Queen Sirikit (BL23)', 22).
fare(bem, 'Silom (BL26)', 'Sam Yan (BL27)', 17).
fare(bem, 'Silom (BL26)', 'Sam Yot (BL30)', 25).
fare(bem, 'Silom (BL26)', 'Sanam Chai (BL31)', 27).
fare(bem, 'Silom (BL26)', 'Sukhumvit (BL22)', 25).
fare(bem, 'Silom (BL26)', 'Wat Mangkon (BL29)', 22).
fare(bem, 'Sukhumvit (BL22)', 'Hua Lamphong (BL28)', 30).
fare(bem, 'Sukhumvit (BL22)', 'Khlong Toei (BL24)', 20).
fare(bem, 'Sukhumvit (BL22)', 'Lumphini (BL25)', 22).
fare(bem, 'Sukhumvit (BL22)', 'Phetchaburi (BL21)', 17).
fare(bem, 'Sukhumvit (BL22)', 'Phra Ram 9 (BL20)', 20).
fare(bem, 'Sukhumvit (BL22)', 'Queen Sirikit (BL23)', 17).
fare(bem, 'Sukhumvit (BL22)', 'Sam Yan (BL27)', 27).
fare(bem, 'Sukhumvit (BL22)', 'Sam Yot (BL30)', 35).
fare(bem, 'Sukhumvit (BL22)', 'Sanam Chai (BL31)', 37).
fare(bem, 'Sukhumvit (BL22)', 'Silom (BL26)', 25).
fare(bem, 'Sukhumvit (BL22)', 'Wat Mangkon (BL29)', 32).
fare(bem, 'Wat Mangkon (BL29)', 'Hua Lamphong (BL28)', 17).
fare(bem, 'Wat Mangkon (BL29)', 'Khlong Toei (BL24)', 27).
fare(bem, 'Wat Mangkon (BL29)', 'Lumphini (BL25)', 25).
fare(bem, 'Wat Mangkon (BL29)', 'Phetchaburi (BL21)', 35).
fare(bem, 'Wat Mangkon (BL29)', 'Phra Ram 9 (BL20)', 37).
fare(bem, 'Wat Mangkon (BL29)', 'Queen Sirikit (BL23)', 30).
fare(bem, 'Wat Mangkon (BL29)', 'Sam Yan (BL27)', 20).
fare(bem, 'Wat Mangkon (BL29)', 'Sam Yot (BL30)', 17).
fare(bem, 'Wat Mangkon (BL29)', 'Sanam Chai (BL31)', 20).
fare(bem, 'Wat Mangkon (BL29)', 'Silom (BL26)', 22).
fare(bem, 'Wat Mangkon (BL29)', 'Sukhumvit (BL22)', 32).

% --- bts (506 fares) ---
fare(bts, 'Ari (N5)', 'Asok (E4)', 47).
fare(bts, 'Ari (N5)', 'Chit Lom (E1)', 40).
fare(bts, 'Ari (N5)', 'Chong Nonsi (S3)', 47).
fare(bts, 'Ari (N5)', 'Ekkamai (E7)', 47).
fare(bts, 'Ari (N5)', 'Mo Chit (N8)', 28).
fare(bts, 'Ari (N5)', 'Nana (E3)', 47).
fare(bts, 'Ari (N5)', 'National Stadium (W1)', 40).
fare(bts, 'Ari (N5)', 'On Nut (E9)', 47).
fare(bts, 'Ari (N5)', 'Phaya Thai (N2)', 28).
fare(bts, 'Ari (N5)', 'Phloen Chit (E2)', 43).
fare(bts, 'Ari (N5)', 'Phra Khanong (E8)', 47).
fare(bts, 'Ari (N5)', 'Phrom Phong (E5)', 47).
fare(bts, 'Ari (N5)', 'Ratchadamri (S1)', 40).
fare(bts, 'Ari (N5)', 'Ratchathevi (N1)', 32).
fare(bts, 'Ari (N5)', 'Sala Daeng (S2)', 43).
fare(bts, 'Ari (N5)', 'Sanam Pao (N4)', 17).
fare(bts, 'Ari (N5)', 'Saphan Khwai (N7)', 25).
fare(bts, 'Ari (N5)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Ari (N5)', 'Siam (CEN)', 35).
fare(bts, 'Ari (N5)', 'Surasak (S5)', 47).
fare(bts, 'Ari (N5)', 'Thong Lo (E6)', 47).
fare(bts, 'Ari (N5)', 'Victory Monument (N3)', 25).
fare(bts, 'Asok (E4)', 'Ari (N5)', 47).
fare(bts, 'Asok (E4)', 'Chit Lom (E1)', 28).
fare(bts, 'Asok (E4)', 'Chong Nonsi (S3)', 43).
fare(bts, 'Asok (E4)', 'Ekkamai (E7)', 28).
fare(bts, 'Asok (E4)', 'Mo Chit (N8)', 47).
fare(bts, 'Asok (E4)', 'Nana (E3)', 17).
fare(bts, 'Asok (E4)', 'National Stadium (W1)', 35).
fare(bts, 'Asok (E4)', 'On Nut (E9)', 35).
fare(bts, 'Asok (E4)', 'Phaya Thai (N2)', 40).
fare(bts, 'Asok (E4)', 'Phloen Chit (E2)', 25).
fare(bts, 'Asok (E4)', 'Phra Khanong (E8)', 32).
fare(bts, 'Asok (E4)', 'Phrom Phong (E5)', 17).
fare(bts, 'Asok (E4)', 'Ratchadamri (S1)', 35).
fare(bts, 'Asok (E4)', 'Ratchathevi (N1)', 35).
fare(bts, 'Asok (E4)', 'Sala Daeng (S2)', 40).
fare(bts, 'Asok (E4)', 'Sanam Pao (N4)', 47).
fare(bts, 'Asok (E4)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Asok (E4)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Asok (E4)', 'Siam (CEN)', 32).
fare(bts, 'Asok (E4)', 'Surasak (S5)', 47).
fare(bts, 'Asok (E4)', 'Thong Lo (E6)', 25).
fare(bts, 'Asok (E4)', 'Victory Monument (N3)', 43).
fare(bts, 'Chit Lom (E1)', 'Ari (N5)', 40).
fare(bts, 'Chit Lom (E1)', 'Asok (E4)', 28).
fare(bts, 'Chit Lom (E1)', 'Chong Nonsi (S3)', 32).
fare(bts, 'Chit Lom (E1)', 'Ekkamai (E7)', 40).
fare(bts, 'Chit Lom (E1)', 'Mo Chit (N8)', 47).
fare(bts, 'Chit Lom (E1)', 'Nana (E3)', 25).
fare(bts, 'Chit Lom (E1)', 'National Stadium (W1)', 25).
fare(bts, 'Chit Lom (E1)', 'On Nut (E9)', 47).
fare(bts, 'Chit Lom (E1)', 'Phaya Thai (N2)', 28).
fare(bts, 'Chit Lom (E1)', 'Phloen Chit (E2)', 17).
fare(bts, 'Chit Lom (E1)', 'Phra Khanong (E8)', 43).
fare(bts, 'Chit Lom (E1)', 'Phrom Phong (E5)', 32).
fare(bts, 'Chit Lom (E1)', 'Ratchadamri (S1)', 25).
fare(bts, 'Chit Lom (E1)', 'Ratchathevi (N1)', 25).
fare(bts, 'Chit Lom (E1)', 'Sala Daeng (S2)', 28).
fare(bts, 'Chit Lom (E1)', 'Sanam Pao (N4)', 35).
fare(bts, 'Chit Lom (E1)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Chit Lom (E1)', 'Saphan Taksin (S6)', 43).
fare(bts, 'Chit Lom (E1)', 'Siam (CEN)', 17).
fare(bts, 'Chit Lom (E1)', 'Surasak (S5)', 40).
fare(bts, 'Chit Lom (E1)', 'Thong Lo (E6)', 35).
fare(bts, 'Chit Lom (E1)', 'Victory Monument (N3)', 32).
fare(bts, 'Chong Nonsi (S3)', 'Ari (N5)', 47).
fare(bts, 'Chong Nonsi (S3)', 'Asok (E4)', 43).
fare(bts, 'Chong Nonsi (S3)', 'Chit Lom (E1)', 32).
fare(bts, 'Chong Nonsi (S3)', 'Ekkamai (E7)', 47).
fare(bts, 'Chong Nonsi (S3)', 'Mo Chit (N8)', 47).
fare(bts, 'Chong Nonsi (S3)', 'Nana (E3)', 40).
fare(bts, 'Chong Nonsi (S3)', 'National Stadium (W1)', 32).
fare(bts, 'Chong Nonsi (S3)', 'On Nut (E9)', 47).
fare(bts, 'Chong Nonsi (S3)', 'Phaya Thai (N2)', 35).
fare(bts, 'Chong Nonsi (S3)', 'Phloen Chit (E2)', 35).
fare(bts, 'Chong Nonsi (S3)', 'Phra Khanong (E8)', 47).
fare(bts, 'Chong Nonsi (S3)', 'Phrom Phong (E5)', 47).
fare(bts, 'Chong Nonsi (S3)', 'Ratchadamri (S1)', 25).
fare(bts, 'Chong Nonsi (S3)', 'Ratchathevi (N1)', 32).
fare(bts, 'Chong Nonsi (S3)', 'Sala Daeng (S2)', 17).
fare(bts, 'Chong Nonsi (S3)', 'Sanam Pao (N4)', 43).
fare(bts, 'Chong Nonsi (S3)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Chong Nonsi (S3)', 'Saphan Taksin (S6)', 28).
fare(bts, 'Chong Nonsi (S3)', 'Siam (CEN)', 28).
fare(bts, 'Chong Nonsi (S3)', 'Surasak (S5)', 25).
fare(bts, 'Chong Nonsi (S3)', 'Thong Lo (E6)', 47).
fare(bts, 'Chong Nonsi (S3)', 'Victory Monument (N3)', 40).
fare(bts, 'Ekkamai (E7)', 'Ari (N5)', 47).
fare(bts, 'Ekkamai (E7)', 'Asok (E4)', 28).
fare(bts, 'Ekkamai (E7)', 'Chit Lom (E1)', 40).
fare(bts, 'Ekkamai (E7)', 'Chong Nonsi (S3)', 47).
fare(bts, 'Ekkamai (E7)', 'Mo Chit (N8)', 47).
fare(bts, 'Ekkamai (E7)', 'Nana (E3)', 32).
fare(bts, 'Ekkamai (E7)', 'National Stadium (W1)', 47).
fare(bts, 'Ekkamai (E7)', 'On Nut (E9)', 25).
fare(bts, 'Ekkamai (E7)', 'Phaya Thai (N2)', 47).
fare(bts, 'Ekkamai (E7)', 'Phloen Chit (E2)', 35).
fare(bts, 'Ekkamai (E7)', 'Phra Khanong (E8)', 17).
fare(bts, 'Ekkamai (E7)', 'Phrom Phong (E5)', 25).
fare(bts, 'Ekkamai (E7)', 'Ratchadamri (S1)', 47).
fare(bts, 'Ekkamai (E7)', 'Ratchathevi (N1)', 47).
fare(bts, 'Ekkamai (E7)', 'Sala Daeng (S2)', 47).
fare(bts, 'Ekkamai (E7)', 'Sanam Pao (N4)', 47).
fare(bts, 'Ekkamai (E7)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Ekkamai (E7)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Ekkamai (E7)', 'Siam (CEN)', 43).
fare(bts, 'Ekkamai (E7)', 'Surasak (S5)', 47).
fare(bts, 'Ekkamai (E7)', 'Thong Lo (E6)', 17).
fare(bts, 'Ekkamai (E7)', 'Victory Monument (N3)', 47).
fare(bts, 'Mo Chit (N8)', 'Ari (N5)', 28).
fare(bts, 'Mo Chit (N8)', 'Asok (E4)', 47).
fare(bts, 'Mo Chit (N8)', 'Chit Lom (E1)', 47).
fare(bts, 'Mo Chit (N8)', 'Chong Nonsi (S3)', 47).
fare(bts, 'Mo Chit (N8)', 'Ekkamai (E7)', 47).
fare(bts, 'Mo Chit (N8)', 'Nana (E3)', 47).
fare(bts, 'Mo Chit (N8)', 'National Stadium (W1)', 47).
fare(bts, 'Mo Chit (N8)', 'On Nut (E9)', 47).
fare(bts, 'Mo Chit (N8)', 'Phaya Thai (N2)', 40).
fare(bts, 'Mo Chit (N8)', 'Phloen Chit (E2)', 47).
fare(bts, 'Mo Chit (N8)', 'Phra Khanong (E8)', 47).
fare(bts, 'Mo Chit (N8)', 'Phrom Phong (E5)', 47).
fare(bts, 'Mo Chit (N8)', 'Ratchadamri (S1)', 47).
fare(bts, 'Mo Chit (N8)', 'Ratchathevi (N1)', 43).
fare(bts, 'Mo Chit (N8)', 'Sala Daeng (S2)', 47).
fare(bts, 'Mo Chit (N8)', 'Sanam Pao (N4)', 32).
fare(bts, 'Mo Chit (N8)', 'Saphan Khwai (N7)', 17).
fare(bts, 'Mo Chit (N8)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Mo Chit (N8)', 'Siam (CEN)', 47).
fare(bts, 'Mo Chit (N8)', 'Surasak (S5)', 47).
fare(bts, 'Mo Chit (N8)', 'Thong Lo (E6)', 47).
fare(bts, 'Mo Chit (N8)', 'Victory Monument (N3)', 35).
fare(bts, 'Nana (E3)', 'Ari (N5)', 47).
fare(bts, 'Nana (E3)', 'Asok (E4)', 17).
fare(bts, 'Nana (E3)', 'Chit Lom (E1)', 25).
fare(bts, 'Nana (E3)', 'Chong Nonsi (S3)', 40).
fare(bts, 'Nana (E3)', 'Ekkamai (E7)', 32).
fare(bts, 'Nana (E3)', 'Mo Chit (N8)', 47).
fare(bts, 'Nana (E3)', 'National Stadium (W1)', 32).
fare(bts, 'Nana (E3)', 'On Nut (E9)', 40).
fare(bts, 'Nana (E3)', 'Phaya Thai (N2)', 35).
fare(bts, 'Nana (E3)', 'Phloen Chit (E2)', 17).
fare(bts, 'Nana (E3)', 'Phra Khanong (E8)', 35).
fare(bts, 'Nana (E3)', 'Phrom Phong (E5)', 25).
fare(bts, 'Nana (E3)', 'Ratchadamri (S1)', 32).
fare(bts, 'Nana (E3)', 'Ratchathevi (N1)', 32).
fare(bts, 'Nana (E3)', 'Sala Daeng (S2)', 35).
fare(bts, 'Nana (E3)', 'Sanam Pao (N4)', 43).
fare(bts, 'Nana (E3)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Nana (E3)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Nana (E3)', 'Siam (CEN)', 28).
fare(bts, 'Nana (E3)', 'Surasak (S5)', 47).
fare(bts, 'Nana (E3)', 'Thong Lo (E6)', 28).
fare(bts, 'Nana (E3)', 'Victory Monument (N3)', 40).
fare(bts, 'National Stadium (W1)', 'Ari (N5)', 40).
fare(bts, 'National Stadium (W1)', 'Asok (E4)', 35).
fare(bts, 'National Stadium (W1)', 'Chit Lom (E1)', 25).
fare(bts, 'National Stadium (W1)', 'Chong Nonsi (S3)', 32).
fare(bts, 'National Stadium (W1)', 'Ekkamai (E7)', 47).
fare(bts, 'National Stadium (W1)', 'Mo Chit (N8)', 47).
fare(bts, 'National Stadium (W1)', 'Nana (E3)', 32).
fare(bts, 'National Stadium (W1)', 'On Nut (E9)', 47).
fare(bts, 'National Stadium (W1)', 'Phaya Thai (N2)', 28).
fare(bts, 'National Stadium (W1)', 'Phloen Chit (E2)', 28).
fare(bts, 'National Stadium (W1)', 'Phra Khanong (E8)', 47).
fare(bts, 'National Stadium (W1)', 'Phrom Phong (E5)', 40).
fare(bts, 'National Stadium (W1)', 'Ratchadamri (S1)', 25).
fare(bts, 'National Stadium (W1)', 'Ratchathevi (N1)', 25).
fare(bts, 'National Stadium (W1)', 'Sala Daeng (S2)', 28).
fare(bts, 'National Stadium (W1)', 'Sanam Pao (N4)', 35).
fare(bts, 'National Stadium (W1)', 'Saphan Khwai (N7)', 47).
fare(bts, 'National Stadium (W1)', 'Saphan Taksin (S6)', 43).
fare(bts, 'National Stadium (W1)', 'Siam (CEN)', 17).
fare(bts, 'National Stadium (W1)', 'Surasak (S5)', 40).
fare(bts, 'National Stadium (W1)', 'Thong Lo (E6)', 43).
fare(bts, 'National Stadium (W1)', 'Victory Monument (N3)', 32).
fare(bts, 'On Nut (E9)', 'Ari (N5)', 47).
fare(bts, 'On Nut (E9)', 'Asok (E4)', 35).
fare(bts, 'On Nut (E9)', 'Chit Lom (E1)', 47).
fare(bts, 'On Nut (E9)', 'Chong Nonsi (S3)', 47).
fare(bts, 'On Nut (E9)', 'Ekkamai (E7)', 25).
fare(bts, 'On Nut (E9)', 'Mo Chit (N8)', 47).
fare(bts, 'On Nut (E9)', 'Nana (E3)', 40).
fare(bts, 'On Nut (E9)', 'National Stadium (W1)', 47).
fare(bts, 'On Nut (E9)', 'Phaya Thai (N2)', 47).
fare(bts, 'On Nut (E9)', 'Phloen Chit (E2)', 43).
fare(bts, 'On Nut (E9)', 'Phra Khanong (E8)', 17).
fare(bts, 'On Nut (E9)', 'Phrom Phong (E5)', 32).
fare(bts, 'On Nut (E9)', 'Ratchadamri (S1)', 47).
fare(bts, 'On Nut (E9)', 'Ratchathevi (N1)', 47).
fare(bts, 'On Nut (E9)', 'Sala Daeng (S2)', 47).
fare(bts, 'On Nut (E9)', 'Sanam Pao (N4)', 47).
fare(bts, 'On Nut (E9)', 'Saphan Khwai (N7)', 47).
fare(bts, 'On Nut (E9)', 'Saphan Taksin (S6)', 47).
fare(bts, 'On Nut (E9)', 'Siam (CEN)', 47).
fare(bts, 'On Nut (E9)', 'Surasak (S5)', 47).
fare(bts, 'On Nut (E9)', 'Thong Lo (E6)', 28).
fare(bts, 'On Nut (E9)', 'Victory Monument (N3)', 47).
fare(bts, 'Phaya Thai (N2)', 'Ari (N5)', 28).
fare(bts, 'Phaya Thai (N2)', 'Asok (E4)', 40).
fare(bts, 'Phaya Thai (N2)', 'Chit Lom (E1)', 28).
fare(bts, 'Phaya Thai (N2)', 'Chong Nonsi (S3)', 35).
fare(bts, 'Phaya Thai (N2)', 'Ekkamai (E7)', 47).
fare(bts, 'Phaya Thai (N2)', 'Mo Chit (N8)', 40).
fare(bts, 'Phaya Thai (N2)', 'Nana (E3)', 35).
fare(bts, 'Phaya Thai (N2)', 'National Stadium (W1)', 28).
fare(bts, 'Phaya Thai (N2)', 'On Nut (E9)', 47).
fare(bts, 'Phaya Thai (N2)', 'Phloen Chit (E2)', 32).
fare(bts, 'Phaya Thai (N2)', 'Phra Khanong (E8)', 47).
fare(bts, 'Phaya Thai (N2)', 'Phrom Phong (E5)', 43).
fare(bts, 'Phaya Thai (N2)', 'Ratchadamri (S1)', 28).
fare(bts, 'Phaya Thai (N2)', 'Ratchathevi (N1)', 17).
fare(bts, 'Phaya Thai (N2)', 'Sala Daeng (S2)', 32).
fare(bts, 'Phaya Thai (N2)', 'Sanam Pao (N4)', 25).
fare(bts, 'Phaya Thai (N2)', 'Saphan Khwai (N7)', 35).
fare(bts, 'Phaya Thai (N2)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Phaya Thai (N2)', 'Siam (CEN)', 25).
fare(bts, 'Phaya Thai (N2)', 'Surasak (S5)', 43).
fare(bts, 'Phaya Thai (N2)', 'Thong Lo (E6)', 47).
fare(bts, 'Phaya Thai (N2)', 'Victory Monument (N3)', 17).
fare(bts, 'Phloen Chit (E2)', 'Ari (N5)', 43).
fare(bts, 'Phloen Chit (E2)', 'Asok (E4)', 25).
fare(bts, 'Phloen Chit (E2)', 'Chit Lom (E1)', 17).
fare(bts, 'Phloen Chit (E2)', 'Chong Nonsi (S3)', 35).
fare(bts, 'Phloen Chit (E2)', 'Ekkamai (E7)', 35).
fare(bts, 'Phloen Chit (E2)', 'Mo Chit (N8)', 47).
fare(bts, 'Phloen Chit (E2)', 'Nana (E3)', 17).
fare(bts, 'Phloen Chit (E2)', 'National Stadium (W1)', 28).
fare(bts, 'Phloen Chit (E2)', 'On Nut (E9)', 43).
fare(bts, 'Phloen Chit (E2)', 'Phaya Thai (N2)', 32).
fare(bts, 'Phloen Chit (E2)', 'Phra Khanong (E8)', 40).
fare(bts, 'Phloen Chit (E2)', 'Phrom Phong (E5)', 28).
fare(bts, 'Phloen Chit (E2)', 'Ratchadamri (S1)', 28).
fare(bts, 'Phloen Chit (E2)', 'Ratchathevi (N1)', 28).
fare(bts, 'Phloen Chit (E2)', 'Sala Daeng (S2)', 32).
fare(bts, 'Phloen Chit (E2)', 'Sanam Pao (N4)', 40).
fare(bts, 'Phloen Chit (E2)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Phloen Chit (E2)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Phloen Chit (E2)', 'Siam (CEN)', 25).
fare(bts, 'Phloen Chit (E2)', 'Surasak (S5)', 43).
fare(bts, 'Phloen Chit (E2)', 'Thong Lo (E6)', 32).
fare(bts, 'Phloen Chit (E2)', 'Victory Monument (N3)', 35).
fare(bts, 'Phra Khanong (E8)', 'Ari (N5)', 47).
fare(bts, 'Phra Khanong (E8)', 'Asok (E4)', 32).
fare(bts, 'Phra Khanong (E8)', 'Chit Lom (E1)', 43).
fare(bts, 'Phra Khanong (E8)', 'Chong Nonsi (S3)', 47).
fare(bts, 'Phra Khanong (E8)', 'Ekkamai (E7)', 17).
fare(bts, 'Phra Khanong (E8)', 'Mo Chit (N8)', 47).
fare(bts, 'Phra Khanong (E8)', 'Nana (E3)', 35).
fare(bts, 'Phra Khanong (E8)', 'National Stadium (W1)', 47).
fare(bts, 'Phra Khanong (E8)', 'On Nut (E9)', 17).
fare(bts, 'Phra Khanong (E8)', 'Phaya Thai (N2)', 47).
fare(bts, 'Phra Khanong (E8)', 'Phloen Chit (E2)', 40).
fare(bts, 'Phra Khanong (E8)', 'Phrom Phong (E5)', 28).
fare(bts, 'Phra Khanong (E8)', 'Ratchadamri (S1)', 47).
fare(bts, 'Phra Khanong (E8)', 'Ratchathevi (N1)', 47).
fare(bts, 'Phra Khanong (E8)', 'Sala Daeng (S2)', 47).
fare(bts, 'Phra Khanong (E8)', 'Sanam Pao (N4)', 47).
fare(bts, 'Phra Khanong (E8)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Phra Khanong (E8)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Phra Khanong (E8)', 'Siam (CEN)', 47).
fare(bts, 'Phra Khanong (E8)', 'Surasak (S5)', 47).
fare(bts, 'Phra Khanong (E8)', 'Thong Lo (E6)', 25).
fare(bts, 'Phra Khanong (E8)', 'Victory Monument (N3)', 47).
fare(bts, 'Phrom Phong (E5)', 'Ari (N5)', 47).
fare(bts, 'Phrom Phong (E5)', 'Asok (E4)', 17).
fare(bts, 'Phrom Phong (E5)', 'Chit Lom (E1)', 32).
fare(bts, 'Phrom Phong (E5)', 'Chong Nonsi (S3)', 47).
fare(bts, 'Phrom Phong (E5)', 'Ekkamai (E7)', 25).
fare(bts, 'Phrom Phong (E5)', 'Mo Chit (N8)', 47).
fare(bts, 'Phrom Phong (E5)', 'Nana (E3)', 25).
fare(bts, 'Phrom Phong (E5)', 'National Stadium (W1)', 40).
fare(bts, 'Phrom Phong (E5)', 'On Nut (E9)', 32).
fare(bts, 'Phrom Phong (E5)', 'Phaya Thai (N2)', 43).
fare(bts, 'Phrom Phong (E5)', 'Phloen Chit (E2)', 28).
fare(bts, 'Phrom Phong (E5)', 'Phra Khanong (E8)', 28).
fare(bts, 'Phrom Phong (E5)', 'Ratchadamri (S1)', 40).
fare(bts, 'Phrom Phong (E5)', 'Ratchathevi (N1)', 40).
fare(bts, 'Phrom Phong (E5)', 'Sala Daeng (S2)', 43).
fare(bts, 'Phrom Phong (E5)', 'Sanam Pao (N4)', 47).
fare(bts, 'Phrom Phong (E5)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Phrom Phong (E5)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Phrom Phong (E5)', 'Siam (CEN)', 35).
fare(bts, 'Phrom Phong (E5)', 'Surasak (S5)', 47).
fare(bts, 'Phrom Phong (E5)', 'Thong Lo (E6)', 17).
fare(bts, 'Phrom Phong (E5)', 'Victory Monument (N3)', 47).
fare(bts, 'Ratchadamri (S1)', 'Ari (N5)', 40).
fare(bts, 'Ratchadamri (S1)', 'Asok (E4)', 35).
fare(bts, 'Ratchadamri (S1)', 'Chit Lom (E1)', 25).
fare(bts, 'Ratchadamri (S1)', 'Chong Nonsi (S3)', 25).
fare(bts, 'Ratchadamri (S1)', 'Ekkamai (E7)', 47).
fare(bts, 'Ratchadamri (S1)', 'Mo Chit (N8)', 47).
fare(bts, 'Ratchadamri (S1)', 'Nana (E3)', 32).
fare(bts, 'Ratchadamri (S1)', 'National Stadium (W1)', 25).
fare(bts, 'Ratchadamri (S1)', 'On Nut (E9)', 47).
fare(bts, 'Ratchadamri (S1)', 'Phaya Thai (N2)', 28).
fare(bts, 'Ratchadamri (S1)', 'Phloen Chit (E2)', 28).
fare(bts, 'Ratchadamri (S1)', 'Phra Khanong (E8)', 47).
fare(bts, 'Ratchadamri (S1)', 'Phrom Phong (E5)', 40).
fare(bts, 'Ratchadamri (S1)', 'Ratchathevi (N1)', 25).
fare(bts, 'Ratchadamri (S1)', 'Sala Daeng (S2)', 17).
fare(bts, 'Ratchadamri (S1)', 'Sanam Pao (N4)', 35).
fare(bts, 'Ratchadamri (S1)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Ratchadamri (S1)', 'Saphan Taksin (S6)', 35).
fare(bts, 'Ratchadamri (S1)', 'Siam (CEN)', 17).
fare(bts, 'Ratchadamri (S1)', 'Surasak (S5)', 32).
fare(bts, 'Ratchadamri (S1)', 'Thong Lo (E6)', 43).
fare(bts, 'Ratchadamri (S1)', 'Victory Monument (N3)', 32).
fare(bts, 'Ratchathevi (N1)', 'Ari (N5)', 32).
fare(bts, 'Ratchathevi (N1)', 'Asok (E4)', 35).
fare(bts, 'Ratchathevi (N1)', 'Chit Lom (E1)', 25).
fare(bts, 'Ratchathevi (N1)', 'Chong Nonsi (S3)', 32).
fare(bts, 'Ratchathevi (N1)', 'Ekkamai (E7)', 47).
fare(bts, 'Ratchathevi (N1)', 'Mo Chit (N8)', 43).
fare(bts, 'Ratchathevi (N1)', 'Nana (E3)', 32).
fare(bts, 'Ratchathevi (N1)', 'National Stadium (W1)', 25).
fare(bts, 'Ratchathevi (N1)', 'On Nut (E9)', 47).
fare(bts, 'Ratchathevi (N1)', 'Phaya Thai (N2)', 17).
fare(bts, 'Ratchathevi (N1)', 'Phloen Chit (E2)', 28).
fare(bts, 'Ratchathevi (N1)', 'Phra Khanong (E8)', 47).
fare(bts, 'Ratchathevi (N1)', 'Phrom Phong (E5)', 40).
fare(bts, 'Ratchathevi (N1)', 'Ratchadamri (S1)', 25).
fare(bts, 'Ratchathevi (N1)', 'Sala Daeng (S2)', 28).
fare(bts, 'Ratchathevi (N1)', 'Sanam Pao (N4)', 28).
fare(bts, 'Ratchathevi (N1)', 'Saphan Khwai (N7)', 40).
fare(bts, 'Ratchathevi (N1)', 'Saphan Taksin (S6)', 43).
fare(bts, 'Ratchathevi (N1)', 'Siam (CEN)', 17).
fare(bts, 'Ratchathevi (N1)', 'Surasak (S5)', 40).
fare(bts, 'Ratchathevi (N1)', 'Thong Lo (E6)', 43).
fare(bts, 'Ratchathevi (N1)', 'Victory Monument (N3)', 25).
fare(bts, 'Sala Daeng (S2)', 'Ari (N5)', 43).
fare(bts, 'Sala Daeng (S2)', 'Asok (E4)', 40).
fare(bts, 'Sala Daeng (S2)', 'Chit Lom (E1)', 28).
fare(bts, 'Sala Daeng (S2)', 'Chong Nonsi (S3)', 17).
fare(bts, 'Sala Daeng (S2)', 'Ekkamai (E7)', 47).
fare(bts, 'Sala Daeng (S2)', 'Mo Chit (N8)', 47).
fare(bts, 'Sala Daeng (S2)', 'Nana (E3)', 35).
fare(bts, 'Sala Daeng (S2)', 'National Stadium (W1)', 28).
fare(bts, 'Sala Daeng (S2)', 'On Nut (E9)', 47).
fare(bts, 'Sala Daeng (S2)', 'Phaya Thai (N2)', 32).
fare(bts, 'Sala Daeng (S2)', 'Phloen Chit (E2)', 32).
fare(bts, 'Sala Daeng (S2)', 'Phra Khanong (E8)', 47).
fare(bts, 'Sala Daeng (S2)', 'Phrom Phong (E5)', 43).
fare(bts, 'Sala Daeng (S2)', 'Ratchadamri (S1)', 17).
fare(bts, 'Sala Daeng (S2)', 'Ratchathevi (N1)', 28).
fare(bts, 'Sala Daeng (S2)', 'Sanam Pao (N4)', 40).
fare(bts, 'Sala Daeng (S2)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Sala Daeng (S2)', 'Saphan Taksin (S6)', 32).
fare(bts, 'Sala Daeng (S2)', 'Siam (CEN)', 25).
fare(bts, 'Sala Daeng (S2)', 'Surasak (S5)', 28).
fare(bts, 'Sala Daeng (S2)', 'Thong Lo (E6)', 47).
fare(bts, 'Sala Daeng (S2)', 'Victory Monument (N3)', 35).
fare(bts, 'Sanam Pao (N4)', 'Ari (N5)', 17).
fare(bts, 'Sanam Pao (N4)', 'Asok (E4)', 47).
fare(bts, 'Sanam Pao (N4)', 'Chit Lom (E1)', 35).
fare(bts, 'Sanam Pao (N4)', 'Chong Nonsi (S3)', 43).
fare(bts, 'Sanam Pao (N4)', 'Ekkamai (E7)', 47).
fare(bts, 'Sanam Pao (N4)', 'Mo Chit (N8)', 32).
fare(bts, 'Sanam Pao (N4)', 'Nana (E3)', 43).
fare(bts, 'Sanam Pao (N4)', 'National Stadium (W1)', 35).
fare(bts, 'Sanam Pao (N4)', 'On Nut (E9)', 47).
fare(bts, 'Sanam Pao (N4)', 'Phaya Thai (N2)', 25).
fare(bts, 'Sanam Pao (N4)', 'Phloen Chit (E2)', 40).
fare(bts, 'Sanam Pao (N4)', 'Phra Khanong (E8)', 47).
fare(bts, 'Sanam Pao (N4)', 'Phrom Phong (E5)', 47).
fare(bts, 'Sanam Pao (N4)', 'Ratchadamri (S1)', 35).
fare(bts, 'Sanam Pao (N4)', 'Ratchathevi (N1)', 28).
fare(bts, 'Sanam Pao (N4)', 'Sala Daeng (S2)', 40).
fare(bts, 'Sanam Pao (N4)', 'Saphan Khwai (N7)', 28).
fare(bts, 'Sanam Pao (N4)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Sanam Pao (N4)', 'Siam (CEN)', 32).
fare(bts, 'Sanam Pao (N4)', 'Surasak (S5)', 47).
fare(bts, 'Sanam Pao (N4)', 'Thong Lo (E6)', 47).
fare(bts, 'Sanam Pao (N4)', 'Victory Monument (N3)', 17).
fare(bts, 'Saphan Khwai (N7)', 'Ari (N5)', 25).
fare(bts, 'Saphan Khwai (N7)', 'Asok (E4)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Chit Lom (E1)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Chong Nonsi (S3)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Ekkamai (E7)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Mo Chit (N8)', 17).
fare(bts, 'Saphan Khwai (N7)', 'Nana (E3)', 47).
fare(bts, 'Saphan Khwai (N7)', 'National Stadium (W1)', 47).
fare(bts, 'Saphan Khwai (N7)', 'On Nut (E9)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Phaya Thai (N2)', 35).
fare(bts, 'Saphan Khwai (N7)', 'Phloen Chit (E2)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Phra Khanong (E8)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Phrom Phong (E5)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Ratchadamri (S1)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Ratchathevi (N1)', 40).
fare(bts, 'Saphan Khwai (N7)', 'Sala Daeng (S2)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Sanam Pao (N4)', 28).
fare(bts, 'Saphan Khwai (N7)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Siam (CEN)', 43).
fare(bts, 'Saphan Khwai (N7)', 'Surasak (S5)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Thong Lo (E6)', 47).
fare(bts, 'Saphan Khwai (N7)', 'Victory Monument (N3)', 32).
fare(bts, 'Saphan Taksin (S6)', 'Ari (N5)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Asok (E4)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Chit Lom (E1)', 43).
fare(bts, 'Saphan Taksin (S6)', 'Chong Nonsi (S3)', 28).
fare(bts, 'Saphan Taksin (S6)', 'Ekkamai (E7)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Mo Chit (N8)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Nana (E3)', 47).
fare(bts, 'Saphan Taksin (S6)', 'National Stadium (W1)', 43).
fare(bts, 'Saphan Taksin (S6)', 'On Nut (E9)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Phaya Thai (N2)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Phloen Chit (E2)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Phra Khanong (E8)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Phrom Phong (E5)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Ratchadamri (S1)', 35).
fare(bts, 'Saphan Taksin (S6)', 'Ratchathevi (N1)', 43).
fare(bts, 'Saphan Taksin (S6)', 'Sala Daeng (S2)', 32).
fare(bts, 'Saphan Taksin (S6)', 'Sanam Pao (N4)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Siam (CEN)', 40).
fare(bts, 'Saphan Taksin (S6)', 'Surasak (S5)', 17).
fare(bts, 'Saphan Taksin (S6)', 'Thong Lo (E6)', 47).
fare(bts, 'Saphan Taksin (S6)', 'Victory Monument (N3)', 47).
fare(bts, 'Siam (CEN)', 'Ari (N5)', 35).
fare(bts, 'Siam (CEN)', 'Asok (E4)', 32).
fare(bts, 'Siam (CEN)', 'Chit Lom (E1)', 17).
fare(bts, 'Siam (CEN)', 'Chong Nonsi (S3)', 28).
fare(bts, 'Siam (CEN)', 'Ekkamai (E7)', 43).
fare(bts, 'Siam (CEN)', 'Mo Chit (N8)', 47).
fare(bts, 'Siam (CEN)', 'Nana (E3)', 28).
fare(bts, 'Siam (CEN)', 'National Stadium (W1)', 17).
fare(bts, 'Siam (CEN)', 'On Nut (E9)', 47).
fare(bts, 'Siam (CEN)', 'Phaya Thai (N2)', 25).
fare(bts, 'Siam (CEN)', 'Phloen Chit (E2)', 25).
fare(bts, 'Siam (CEN)', 'Phra Khanong (E8)', 47).
fare(bts, 'Siam (CEN)', 'Phrom Phong (E5)', 35).
fare(bts, 'Siam (CEN)', 'Ratchadamri (S1)', 17).
fare(bts, 'Siam (CEN)', 'Ratchathevi (N1)', 17).
fare(bts, 'Siam (CEN)', 'Sala Daeng (S2)', 25).
fare(bts, 'Siam (CEN)', 'Sanam Pao (N4)', 32).
fare(bts, 'Siam (CEN)', 'Saphan Khwai (N7)', 43).
fare(bts, 'Siam (CEN)', 'Saphan Taksin (S6)', 40).
fare(bts, 'Siam (CEN)', 'Surasak (S5)', 35).
fare(bts, 'Siam (CEN)', 'Thong Lo (E6)', 40).
fare(bts, 'Siam (CEN)', 'Victory Monument (N3)', 28).
fare(bts, 'Surasak (S5)', 'Ari (N5)', 47).
fare(bts, 'Surasak (S5)', 'Asok (E4)', 47).
fare(bts, 'Surasak (S5)', 'Chit Lom (E1)', 40).
fare(bts, 'Surasak (S5)', 'Chong Nonsi (S3)', 25).
fare(bts, 'Surasak (S5)', 'Ekkamai (E7)', 47).
fare(bts, 'Surasak (S5)', 'Mo Chit (N8)', 47).
fare(bts, 'Surasak (S5)', 'Nana (E3)', 47).
fare(bts, 'Surasak (S5)', 'National Stadium (W1)', 40).
fare(bts, 'Surasak (S5)', 'On Nut (E9)', 47).
fare(bts, 'Surasak (S5)', 'Phaya Thai (N2)', 43).
fare(bts, 'Surasak (S5)', 'Phloen Chit (E2)', 43).
fare(bts, 'Surasak (S5)', 'Phra Khanong (E8)', 47).
fare(bts, 'Surasak (S5)', 'Phrom Phong (E5)', 47).
fare(bts, 'Surasak (S5)', 'Ratchadamri (S1)', 32).
fare(bts, 'Surasak (S5)', 'Ratchathevi (N1)', 40).
fare(bts, 'Surasak (S5)', 'Sala Daeng (S2)', 28).
fare(bts, 'Surasak (S5)', 'Sanam Pao (N4)', 47).
fare(bts, 'Surasak (S5)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Surasak (S5)', 'Saphan Taksin (S6)', 17).
fare(bts, 'Surasak (S5)', 'Siam (CEN)', 35).
fare(bts, 'Surasak (S5)', 'Thong Lo (E6)', 47).
fare(bts, 'Surasak (S5)', 'Victory Monument (N3)', 47).
fare(bts, 'Thong Lo (E6)', 'Ari (N5)', 47).
fare(bts, 'Thong Lo (E6)', 'Asok (E4)', 25).
fare(bts, 'Thong Lo (E6)', 'Chit Lom (E1)', 35).
fare(bts, 'Thong Lo (E6)', 'Chong Nonsi (S3)', 47).
fare(bts, 'Thong Lo (E6)', 'Ekkamai (E7)', 17).
fare(bts, 'Thong Lo (E6)', 'Mo Chit (N8)', 47).
fare(bts, 'Thong Lo (E6)', 'Nana (E3)', 28).
fare(bts, 'Thong Lo (E6)', 'National Stadium (W1)', 43).
fare(bts, 'Thong Lo (E6)', 'On Nut (E9)', 28).
fare(bts, 'Thong Lo (E6)', 'Phaya Thai (N2)', 47).
fare(bts, 'Thong Lo (E6)', 'Phloen Chit (E2)', 32).
fare(bts, 'Thong Lo (E6)', 'Phra Khanong (E8)', 25).
fare(bts, 'Thong Lo (E6)', 'Phrom Phong (E5)', 17).
fare(bts, 'Thong Lo (E6)', 'Ratchadamri (S1)', 43).
fare(bts, 'Thong Lo (E6)', 'Ratchathevi (N1)', 43).
fare(bts, 'Thong Lo (E6)', 'Sala Daeng (S2)', 47).
fare(bts, 'Thong Lo (E6)', 'Sanam Pao (N4)', 47).
fare(bts, 'Thong Lo (E6)', 'Saphan Khwai (N7)', 47).
fare(bts, 'Thong Lo (E6)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Thong Lo (E6)', 'Siam (CEN)', 40).
fare(bts, 'Thong Lo (E6)', 'Surasak (S5)', 47).
fare(bts, 'Thong Lo (E6)', 'Victory Monument (N3)', 47).
fare(bts, 'Victory Monument (N3)', 'Ari (N5)', 25).
fare(bts, 'Victory Monument (N3)', 'Asok (E4)', 43).
fare(bts, 'Victory Monument (N3)', 'Chit Lom (E1)', 32).
fare(bts, 'Victory Monument (N3)', 'Chong Nonsi (S3)', 40).
fare(bts, 'Victory Monument (N3)', 'Ekkamai (E7)', 47).
fare(bts, 'Victory Monument (N3)', 'Mo Chit (N8)', 35).
fare(bts, 'Victory Monument (N3)', 'Nana (E3)', 40).
fare(bts, 'Victory Monument (N3)', 'National Stadium (W1)', 32).
fare(bts, 'Victory Monument (N3)', 'On Nut (E9)', 47).
fare(bts, 'Victory Monument (N3)', 'Phaya Thai (N2)', 17).
fare(bts, 'Victory Monument (N3)', 'Phloen Chit (E2)', 35).
fare(bts, 'Victory Monument (N3)', 'Phra Khanong (E8)', 47).
fare(bts, 'Victory Monument (N3)', 'Phrom Phong (E5)', 47).
fare(bts, 'Victory Monument (N3)', 'Ratchadamri (S1)', 32).
fare(bts, 'Victory Monument (N3)', 'Ratchathevi (N1)', 25).
fare(bts, 'Victory Monument (N3)', 'Sala Daeng (S2)', 35).
fare(bts, 'Victory Monument (N3)', 'Sanam Pao (N4)', 17).
fare(bts, 'Victory Monument (N3)', 'Saphan Khwai (N7)', 32).
fare(bts, 'Victory Monument (N3)', 'Saphan Taksin (S6)', 47).
fare(bts, 'Victory Monument (N3)', 'Siam (CEN)', 28).
fare(bts, 'Victory Monument (N3)', 'Surasak (S5)', 47).
fare(bts, 'Victory Monument (N3)', 'Thong Lo (E6)', 47).

% --- srtet (6 fares) ---
fare(srtet, 'Makkasan (A6)', 'Phaya Thai (A8)', 20).
fare(srtet, 'Makkasan (A6)', 'Ratchaprarop (A7)', 15).
fare(srtet, 'Phaya Thai (A8)', 'Makkasan (A6)', 20).
fare(srtet, 'Phaya Thai (A8)', 'Ratchaprarop (A7)', 15).
fare(srtet, 'Ratchaprarop (A7)', 'Makkasan (A6)', 15).
fare(srtet, 'Ratchaprarop (A7)', 'Phaya Thai (A8)', 15).
