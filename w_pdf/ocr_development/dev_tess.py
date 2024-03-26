"""

tesseract 5
https://tesseract-docs.readthedocs.io/_/downloads/en/latest/pdf/

**ALL CONFIGS LOADED INTO:
claude optimizing iron tesseract OCR with config parameters**



tessedit_pageseg_mode 1
tessedit_ocr_engine_mode 1
tessedit_char_whitelist 0123456789
tessedit_char_blacklist ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz

*Increase lstm_choice_iterations for more accurate but slower OCR

seg mode:
0    Orientation and script detection (OSD) only.
1    Automatic page segmentation with OSD.
2    Automatic page segmentation, but no OSD, or OCR.
3    Fully automatic page segmentation, but no OSD. (Default)
4    Assume a single column of text of variable sizes.
5    Assume a single uniform block of vertically aligned text.
6    Assume a single uniform block of text. 
7    Treat the image as a single text line.
8    Treat the image as a single word.
9    Treat the image as a single word in a circle.
10    Treat the image as a single character.



tess 5:
    VIA:
    https://tesseract-ocr.github.io/tessapi/5.x/a02658.html


No problem! Let's focus on the key Tesseract 5 configuration options:

pageseg_mode - Page segmentation mode
oem - OCR engine mode
tessedit_char_blacklist - Blacklist characters
tessedit_char_whitelist - Whitelist characters
tessedit_pageseg_mode - Alternative for pageseg_mode
tessedit_ocr_engine_mode - Alternative for oem
tessedit_write_images - Capture intermediate images
tessedit_create_tsv - Create TSV output
tessedit_create_txt - Create plain text output
tessedit_create_hocr - Create HOCR output
tessedit_create_alto - Create ALTO XML output
tessedit_create_lstmbox - Create LSTM training data
tessedit_page_number - Process specific page number
lstm_choice_mode - Include alternative OCR choices
lstm_choice_iterations - Number of iterations for lstm choices
lstm_rating_coefficient - Rating coefficient for lstm choices
The most important ones being:

pageseg_mode - To control layout analysis
oem - To set OCR engine mode
Blacklist/whitelist - To filter characters
Output format - Like TSV, HOCR, etc






The oem (OCR engine mode) parameter in Tesseract controls which recognition engine(s) will be used. The possible values are:

0 - Legacy Tesseract-only OCR engine
1 - Neural network LSTM-only OCR engine
2 - Legacy + LSTM engines (default, picks the best result)
3 - Legacy Tesseract engine forced without tuning (for testing)

So in summary:

oem 0 = Use only the traditional Tesseract OCR engine
oem 1 = Use only the LSTM neural network engine

The default oem 2 runs both and picks the best result.

oem 0 (Tesseract-only) provides better performance on simpler print-quality documents but lower accuracy on complex layouts.

oem 1 (LSTM-only) works better for handwriting and complex documents but can be slower.

So switching oem allows you to choose between the traditional Tesseract engine vs the newer LSTM engine depending on your use case. The default oem 2 gives the flexibility to use both.




    

Public Attributes
bool 	tessedit_resegment_from_boxes = false
 
bool 	tessedit_resegment_from_line_boxes = false
 
bool 	tessedit_train_from_boxes = false
 
bool 	tessedit_make_boxes_from_boxes = false
 
bool 	tessedit_train_line_recognizer = false
 
bool 	tessedit_dump_pageseg_images = false
 
bool 	tessedit_do_invert = true
 
int 	tessedit_pageseg_mode = PSM_SINGLE_BLOCK
 
int 	tessedit_ocr_engine_mode = tesseract::OEM_DEFAULT
 
char * 	tessedit_char_blacklist = ""
 
char * 	tessedit_char_whitelist = ""
 
char * 	tessedit_char_unblacklist = ""
 
bool 	tessedit_ambigs_training = false
 
int 	pageseg_devanagari_split_strategy = tesseract::ShiroRekhaSplitter::NO_SPLIT
 
int 	ocr_devanagari_split_strategy = tesseract::ShiroRekhaSplitter::NO_SPLIT
 
char * 	tessedit_write_params_to_file = ""
 
bool 	tessedit_adaption_debug = false
 
int 	bidi_debug = 0
 
int 	applybox_debug = 1
 
int 	applybox_page = 0
 
char * 	applybox_exposure_pattern = ".exp"
 
bool 	applybox_learn_chars_and_char_frags_mode = false
 
bool 	applybox_learn_ngrams_mode = false
 
bool 	tessedit_display_outwords = false
 
bool 	tessedit_dump_choices = false
 
bool 	tessedit_timing_debug = false
 
bool 	tessedit_fix_fuzzy_spaces = true
 
bool 	tessedit_unrej_any_wd = false
 
bool 	tessedit_fix_hyphens = true
 
bool 	tessedit_enable_doc_dict = true
 
bool 	tessedit_debug_fonts = false
 
bool 	tessedit_debug_block_rejection = false
 
bool 	tessedit_enable_bigram_correction = true
 
bool 	tessedit_enable_dict_correction = false
 
int 	tessedit_bigram_debug = 0
 
bool 	enable_noise_removal = true
 
int 	debug_noise_removal = 0
 
double 	noise_cert_basechar = -8.0
 
double 	noise_cert_disjoint = -2.5
 
double 	noise_cert_punc = -2.5
 
double 	noise_cert_factor = 0.375
 
int 	noise_maxperblob = 8
 
int 	noise_maxperword = 16
 
int 	debug_x_ht_level = 0
 
char * 	chs_leading_punct = "('`\""
 
char * 	chs_trailing_punct1 = ").,;:?!"
 
char * 	chs_trailing_punct2 = ")'`\""
 
double 	quality_rej_pc = 0.08
 
double 	quality_blob_pc = 0.0
 
double 	quality_outline_pc = 1.0
 
double 	quality_char_pc = 0.95
 
int 	quality_min_initial_alphas_reqd = 2
 
int 	tessedit_tess_adaption_mode = 0x27
 
bool 	tessedit_minimal_rej_pass1 = false
 
bool 	tessedit_test_adaption = false
 
bool 	test_pt = false
 
double 	test_pt_x = 99999.99
 
double 	test_pt_y = 99999.99
 
int 	multilang_debug_level = 0
 
int 	paragraph_debug_level = 0
 
bool 	paragraph_text_based = true
 
bool 	lstm_use_matrix = 1
 
char * 	outlines_odd = "%| "
 
char * 	outlines_2 = "ij!?%\":;"
 
bool 	tessedit_good_quality_unrej = true
 
bool 	tessedit_use_reject_spaces = true
 
double 	tessedit_reject_doc_percent = 65.00
 
double 	tessedit_reject_block_percent = 45.00
 
double 	tessedit_reject_row_percent = 40.00
 
double 	tessedit_whole_wd_rej_row_percent = 70.00
 
bool 	tessedit_preserve_blk_rej_perfect_wds = true
 
bool 	tessedit_preserve_row_rej_perfect_wds = true
 
bool 	tessedit_dont_blkrej_good_wds = false
 
bool 	tessedit_dont_rowrej_good_wds = false
 
int 	tessedit_preserve_min_wd_len = 2
 
bool 	tessedit_row_rej_good_docs = true
 
double 	tessedit_good_doc_still_rowrej_wd = 1.1
 
bool 	tessedit_reject_bad_qual_wds = true
 
bool 	tessedit_debug_doc_rejection = false
 
bool 	tessedit_debug_quality_metrics = false
 
bool 	bland_unrej = false
 
double 	quality_rowrej_pc = 1.1
 
bool 	unlv_tilde_crunching = false
 
bool 	hocr_font_info = false
 
bool 	hocr_char_boxes = false
 
bool 	crunch_early_merge_tess_fails = true
 
bool 	crunch_early_convert_bad_unlv_chs = false
 
double 	crunch_terrible_rating = 80.0
 
bool 	crunch_terrible_garbage = true
 
double 	crunch_poor_garbage_cert = -9.0
 
double 	crunch_poor_garbage_rate = 60
 
double 	crunch_pot_poor_rate = 40
 
double 	crunch_pot_poor_cert = -8.0
 
double 	crunch_del_rating = 60
 
double 	crunch_del_cert = -10.0
 
double 	crunch_del_min_ht = 0.7
 
double 	crunch_del_max_ht = 3.0
 
double 	crunch_del_min_width = 3.0
 
double 	crunch_del_high_word = 1.5
 
double 	crunch_del_low_word = 0.5
 
double 	crunch_small_outlines_size = 0.6
 
int 	crunch_rating_max = 10
 
int 	crunch_pot_indicators = 1
 
bool 	crunch_leave_ok_strings = true
 
bool 	crunch_accept_ok = true
 
bool 	crunch_leave_accept_strings = false
 
bool 	crunch_include_numerals = false
 
int 	crunch_leave_lc_strings = 4
 
int 	crunch_leave_uc_strings = 4
 
int 	crunch_long_repetitions = 3
 
int 	crunch_debug = 0
 
int 	fixsp_non_noise_limit = 1
 
double 	fixsp_small_outlines_size = 0.28
 
bool 	tessedit_prefer_joined_punct = false
 
int 	fixsp_done_mode = 1
 
int 	debug_fix_space_level = 0
 
char * 	numeric_punctuation = ".,"
 
int 	x_ht_acceptance_tolerance = 8
 
int 	x_ht_min_change = 8
 
int 	superscript_debug = 0
 
double 	superscript_worse_certainty = 2.0
 
double 	superscript_bettered_certainty = 0.97
 
double 	superscript_scaledown_ratio = 0.4
 
double 	subscript_max_y_top = 0.5
 
double 	superscript_min_y_bottom = 0.3
 
bool 	tessedit_write_block_separators = false
 
bool 	tessedit_write_rep_codes = false
 
bool 	tessedit_write_unlv = false
 
bool 	tessedit_create_txt = false
 
bool 	tessedit_create_hocr = false
 
bool 	tessedit_create_alto = false
 
bool 	tessedit_create_lstmbox = false
 
bool 	tessedit_create_tsv = false
 
bool 	tessedit_create_wordstrbox = false
 
bool 	tessedit_create_pdf = false
 
bool 	textonly_pdf = false
 
int 	jpg_quality = 85
 
int 	user_defined_dpi = 0
 
int 	min_characters_to_try = 50
 
char * 	unrecognised_char = "|"
 
int 	suspect_level = 99
 
int 	suspect_short_words = 2
 
bool 	suspect_constrain_1Il = false
 
double 	suspect_rating_per_ch = 999.9
 
double 	suspect_accept_rating = -999.9
 
bool 	tessedit_minimal_rejection = false
 
bool 	tessedit_zero_rejection = false
 
bool 	tessedit_word_for_word = false
 
bool 	tessedit_zero_kelvin_rejection = false
 
int 	tessedit_reject_mode = 0
 
bool 	tessedit_rejection_debug = false
 
bool 	tessedit_flip_0O = true
 
double 	tessedit_lower_flip_hyphen = 1.5
 
double 	tessedit_upper_flip_hyphen = 1.8
 
bool 	rej_trust_doc_dawg = false
 
bool 	rej_1Il_use_dict_word = false
 
bool 	rej_1Il_trust_permuter_type = true
 
bool 	rej_use_tess_accepted = true
 
bool 	rej_use_tess_blanks = true
 
bool 	rej_use_good_perm = true
 
bool 	rej_use_sensible_wd = false
 
bool 	rej_alphas_in_number_perm = false
 
double 	rej_whole_of_mostly_reject_word_fract = 0.85
 
int 	tessedit_image_border = 2
 
char * 	ok_repeated_ch_non_alphanum_wds = "-?*\075"
 
char * 	conflict_set_I_l_1 = "Il1[]"
 
int 	min_sane_x_ht_pixels = 8
 
bool 	tessedit_create_boxfile = false
 
int 	tessedit_page_number = -1
 
bool 	tessedit_write_images = false
 
bool 	interactive_display_mode = false
 
char * 	file_type = ".tif"
 
bool 	tessedit_override_permuter = true
 
char * 	tessedit_load_sublangs = ""
 
bool 	tessedit_use_primary_params_model = false
 
double 	min_orientation_margin = 7.0
 
bool 	textord_tabfind_show_vlines = false
 
bool 	textord_use_cjk_fp_model = false
 
bool 	poly_allow_detailed_fx = false
 
bool 	tessedit_init_config_only = false
 
bool 	textord_equation_detect = false
 
bool 	textord_tabfind_vertical_text = true
 
bool 	textord_tabfind_force_vertical_text = false
 
double 	textord_tabfind_vertical_text_ratio = 0.5
 
double 	textord_tabfind_aligned_gap_fraction = 0.75
 
int 	tessedit_parallelize = 0
 
bool 	preserve_interword_spaces = false
 
char * 	page_separator = "\f"
 
int 	lstm_choice_mode = 0
 
int 	lstm_choice_iterations = 5
 
double 	lstm_rating_coefficient = 5
 
bool 	pageseg_apply_music_mask = true

"""