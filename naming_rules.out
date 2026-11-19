NAMING RULES FOR THE THESIS MATERIAL DIRECTORY
Applied on 2026-11-19. Scope and rules agreed with the owner of this directory.

1. SCOPE
   Renamed: every PDF (papers, reports, theses, books, book chapters, saved web page printouts)
   and the directory names listed in section 8.
   Left untouched:
   - confluence_pages/
   - configuration_optimization/viscous_models/mit_mark_drela_course/ (scraped site, videos, its PDFs)
   - automatic_differentiation/mit_course/ (course slides)
   - the saved web page asset directory "fluid dynamics ..._files/"
   - non PDF files (ibl3_errata.txt, prompt, the empty file x, this file)

2. FILENAME FORMAT
   <title_snake>_<Surname1>[_<Surname2>[_<Surname3>]][_et_al]_<year>.pdf
   Example: quasi-three-dimensional_aerodynamic_solver_for_multidisciplinary_design_optimization_of_lifting_surfaces_Mariens_Elham_van_Tooren_2014.pdf

3. TITLE RULES
   3.1 The title is the real published title read from the first page of the document, not the old
       filename. Truncated titles, typos, hash tails (_2QUz, _v0LA), URL slugs, publisher prefixes and
       informal labels (basics_vlm, MDOSurvey, naca0015_validation, Johnston triangular-hodograph,
       georgia_tech_BL_Goldstein_singularity, snel_empirical_correction_of_himmelskamp_effect)
       are replaced by the actual title.
   3.2 Lowercase, words joined by single underscores. Proper nouns that are not acronyms are lowercased
       (reynolds, mach, galerkin, navier-stokes, von_karman, falkner-skan, squire-young, stokes).
       Product names are lowercased too (flightstream), except where listed in 3.4.
   3.3 Hyphenated words keep their hyphen (viscous-inviscid, blade-element, gradient-based, aerodynamic-like).
       Unicode hyphens and dashes (U+2010, U+2011, en dash) become the ASCII hyphen.
       Numeric ranges keep the hyphen (1920-1950).
   3.4 Acronyms stay capitalised: BEMT, MDAO, MDO, UAV, RANS, NACA, NASA, AIAA, XFOIL, VSPAERO, IBL3, Q3D,
       BL3D, F50, VLM, DG, FAST, RCAIDE, MBSE, INCOSE, CFD, TU, Delft (accepted 2026-11-19, as in TU_Delft),
       2D, 2.5D, 3D, and the roman numeral I.
       eN (the e to the N transition method) stays exactly as eN.
       The authoritative list is tools/paperlib/src/paperlib/acronyms.txt, used by paper and papis to build names.
       A title token matches an entry when it is written exactly like it or in all caps; entries starting with a
       digit and deal.II match in any case. All caps tokens not on the list stop `paper add` until added or lowercased.
       deal.II keeps its dot and official spelling (lowercase deal, capital II).
   3.5 Decimal points between digits are kept (0.8 stays 0.8, 0.96 stays 0.96). Dots in deal.II and 2.5D are kept.
   3.6 All other punctuation is removed: : , ; ( ) ' " ? ! and other dots. Content in parentheses stays as words
       (..._tool_FAST_...). & becomes and. Abbreviations are expanded (w becomes with).
       Subtitles are joined to the title with a single underscore.
   3.7 Spelling variants of the published title are kept (optimisation vs optimization).
   3.8 Book chapters use the chapter title only. The book name lives in the directory name.
   3.9 Maximum 255 bytes per name (longest used: 178).

4. AUTHOR RULES
   4.1 Surnames only, original capitalisation, paper order, at most three.
       More than three authors: first three surnames, then _et_al.
   4.2 Name particles are joined to the surname with underscores (van_Tooren, van_Ingen, van_der_Vorst, von_Karman).
       Compound surnames are one surname (Ramos_Garcia, Garcia_Rodriguez).
       Hyphenated surnames keep the hyphen (Vaziry-Zanjany).
   4.3 Diacritics are folded to ASCII (Marien, Ruter, Bendsoe, Sorensen). Name suffixes such as Jr are dropped.
   4.4 Repeated surnames are kept as they appear (Dilgen_Dilgen_Fuhrman_et_al).
   4.5 Edited volumes use the editor (low_reynolds_number_aerodynamics_Mueller_1989).
   4.6 No personal author: the organisation or site name is used (NASA, Research_in_Flight, stackexchange).
   4.7 Lecture notes without a printed author use the lecturer (Drela).

5. YEAR RULES
   5.1 Publication year of the content. PDF metadata and download stamps are never used (many show 2026).
   5.2 Journal articles use the volume year, not the online first or file date.
   5.3 Translated or reprinted classics use the ORIGINAL year, not the translation year:
       Prandtl 1904 (NACA TM 452), von Karman 1921 (NACA TM 1092), Pohlhausen 1921 (1965 translation),
       Schlichting 1942 (NACA TM 1217, lectures 1941/42), Goldstein 1948.
   5.4 Books use the edition year of the copy in hand (Anderson 2021 4th ed, Schlichting_Gersten 2017 9th ed,
       Bendsoe_Sigmund 2004 corrected printing, Martins_Ning 2021 print edition).
   5.5 Saved web pages use the year the question was asked (stackexchange 2013, 2022).
       A manual without a date uses its print or access year (flightstream manual 2026).
   5.6 Encyclopedia chapters use 2017.

6. DUPLICATES
   Same document in several places: keep the larger file, in the most appropriate directory, delete the rest.
   Removed on 2026-11-19 (all verified by identical text or identical bytes first):
   - viscous_models/3d/The law of the wake in the turbulent boundary layer.pdf (identical to the Coles copy kept)
   - configuration_optimization/FE/Encyclopedia ... Cockburn ....pdf (the books/ copy is larger), then the empty FE/ dir
   - top level Viscous-Inviscid_Analysis_of_Transonic_and_Low_Rey.pdf (the viscous_models/ copy is larger)
   - viscous_models/On laminar boundary-layer flow near a position of separation.pdf (the Goldstein copy in
     classical_BL_theory_papers/ is larger)

7. COLLISIONS
   A new name must be unique in its directory. Moves are done without clobbering and abort if the target exists.

8. DIRECTORY RULES
   Same snake_case and acronym rules, no author or year.
   Changed:
   - viscous_models/3d  -> viscous_models/3D
   - viscous_models/2.5d -> viscous_models/2.5D
   - books/Encyclopedia of Computational Mechanics -> books/encyclopedia_of_computational_mechanics
   - FE removed (it only held the duplicate)
   Unchanged because they already comply: BEMT, automatic_differentiation, configuration_optimization,
   topology_optimization, viscous_models, mission_simulation, supersonic_props, classical_BL_theory_papers, books.

9. ENTRIES WITH LOWER CONFIDENCE (author or year not fully printed on the document)
   - the_dynamics_and_thermodynamics_of_compressible_fluid_flow_Shapiro_1953 (scan, from memory)
   - propellers_at_high_speeds_Draley_1947 (year confirmed by the owner)
   - a_modified_geometry_based_analytical_model_of_..._Vadamodala_Das_Chowdhury_et_al_2022 (authors from the owner)
   - von-karman_compressible_integral_momentum_and_kinetic_energy_equations_..._Drela_2003 (course note, author and year inferred)
   - boundary_layers_Lautrup_2004 (chapter 25 of Physics of Continuous Matter)
   - the_high-speed_frontier_case_histories_of_four_NACA_programs_1920-1950_Becker_1980 (year from memory)
   - several 2013 to 2025 journal years taken from DOI or journal volume (see rename_map.tsv notes in the session scratchpad)
   - RCAIDE_..._Clarke_Guidotti_Shekar_et_al_2026: renamed on 2026-11-19 from ..._Clarke_Guidotti_Boggan_et_al_2026
     after the Crossref author order check (Clarke, Guidotti, Shekar, Molloy, Boggan, Guerrero).

11. LIBRARY LAYOUT (papis, from 2026-11-19)
   Each paper lives in its own folder named like the PDF: <topic dirs>/<name>/<name>.pdf, with info.yaml (metadata)
   and fulltext.txt (pdftotext output, created once, OCR first for scans). Names are generated from info.yaml
   (title, author_list, year) by tools/paperlib; the pre-commit hook refuses folders or PDFs whose name differs.
   Documents whose metadata did not come from a DOI on the PDF carry the tag needs-review.

10. VERIFICATION DONE
   - 99 PDFs in scope before, 95 after (4 duplicates deleted).
   - md5 of all 95 renamed files equals the md5 before the move.
   - Every in scope name matches ^[A-Za-z0-9][A-Za-z0-9._-]*_(19|20)dd.pdf$ with no spaces or non ASCII characters.
   - The excluded mit_mark_drela_course tree still holds its 559 files.
