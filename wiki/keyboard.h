/*
 * Copyright (c) 2009 Openmoko Inc.
 *
 * Authors   Holger Hans Peter Freyther <zecke@openmoko.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef WL_KEYBOARD_H
#define WL_KEYBOARD_H

/**
 * keyboard functionality
 */

#define KEYBOARD_WIDTH	240
#define KEYBOARD_HEIGHT	82
#define INITIAL_JAMO_COUNT 19
#define MIDDLE_JAMO_COUNT 21
#define FINAL_JAMO_COUNT 28

#define WL_KEY_TEMPERATURE			0X0B
#define WL_KEY_CLEAR				0X0A
#define WL_KEY_BACKWARD				0X09
#define WL_KEY_BACKSPACE			0x08
#define WL_KEY_NLS				0x07
#define WL_KEY_SWITCH_KEYBOARD 			0x06
#define WL_KEY_POHONE_STYLE_KEYBOARD_DEFAULT 	0x05
#define WL_KEY_POHONE_STYLE_KEYBOARD_ABC	0X04
#define WL_KEY_POHONE_STYLE_KEYBOARD_123	0X03
#define WL_KEY_SONANT 				0X02
#define WL_KEY_NO_WAIT 				0X01

#define WL_KEY_TEMPERATURE_STR				"\x0B\x00"
#define WL_KEY_CLEAR_STR				"\x0A\x00"
#define WL_KEY_BACKWARD_STR				"\x09\x00"
#define WL_KEY_BACKSPACE_STR				"\x08\x00"
#define WL_KEY_NLS_STR					"\x07\x00"
#define WL_KEY_SWITCH_KEYBOARD_STR 			"\x06\x00"
#define WL_KEY_POHONE_STYLE_KEYBOARD_DEFAULT_STR 	"\x05\x00"
#define WL_KEY_POHONE_STYLE_KEYBOARD_ABC_STR 		"\x04\x00"
#define WL_KEY_POHONE_STYLE_KEYBOARD_123_STR 		"\x03\x00"
#define WL_KEY_SONANT_STR				"\x02\x00"
#define WL_KEY_NO_WAIT_STR				"\x01\x00"

typedef enum {
	KEYBOARD_NONE,
	KEYBOARD_CHAR,
	KEYBOARD_CHAR_JP,
	KEYBOARD_CHAR_KO,
	KEYBOARD_CHAR_DA,
	KEYBOARD_NUM,
	// all non-phone style keyboards for search should be before this
	KEYBOARD_PHONE_STYLE,
	// all phone style keyboards should be after this
	KEYBOARD_PHONE_STYLE_JP,
	KEYBOARD_PHONE_STYLE_TW,
	KEYBOARD_PHONE_STYLE_ABC,
	KEYBOARD_PHONE_STYLE_123,
	KEYBOARD_CLEAR_HISTORY,
	KEYBOARD_RESTRICTED,
	KEYBOARD_PASSWORD_CHAR,
	KEYBOARD_PASSWORD_NUM,
	KEYBOARD_FILTER_ON_OFF,
	KEYBOARD_FILTER_OPTION
} KEYBOARD_MODE;

enum {
	KEYBOARD_RESET_INVERT_DELAY,
	KEYBOARD_RESET_INVERT_NOW,
	KEYBOARD_RESET_INVERT_CHECK
};

struct keyboard_key {
	/*
	 * a rect described by top left and
	 * bottom right point.
	 */
	int left_x, right_x;
	int left_y, right_y;
	int left_x_inverted, right_x_inverted;
	int left_y_inverted, right_y_inverted;
	const unsigned char *key; // assuming non-multi-selection key should have length = 1
};

void keyboard_set_mode(int mode);
int keyboard_get_mode();
unsigned int keyboard_height();
void keyboard_paint();
struct keyboard_key * keyboard_get_data(int x, int y);
void keyboard_key_invert(struct keyboard_key *key);
int keyboard_key_reset_invert(int bFlag, unsigned long ev_time);
int keyboard_key_inverted(void);
int keyboard_adjacent_keys(struct keyboard_key *key1, struct keyboard_key *key2);
struct keyboard_key *keyboard_locate_key(char keycode);
void flash_keyboard_key_invert();
int multi_selection_key(struct keyboard_key *key);
int keyboard_korean_special_key(void);
int is_korean_special_key_enabled(void);
int temperature_button_enabled(void);
unsigned char *temperature_string(void);
void draw_temperature(void);
void get_temperature_mode(void);
void set_temperature_mode(void);
#endif
