/*
 * binary search 
 * (C) Copyright 2008 OpenMoko, Inc.
 * Author: xiangfu liu <xiangfu@openmoko.org>
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

#include <t_services.h>
#include "search.h"
#include "sample1.h"
#include <tff.h>
#include <stdio.h>
#include <string.h>

#define MAXWORDS 100 	/* line count of the index file */
#define SHA1CHARS 40		/* sha1 char count */
#define MAXCHARS 40		/* the max chars of the title */
#define LINECHARS 80
#define RESULTCOUNT 10

int g_titles_count = 0; 
char *g_titles[MAXWORDS] , *g_hash[MAXWORDS], *g_result[RESULTCOUNT];
int g_result_index = -1;/* use this store the result index. not value */

int split(char *source, char *word, char *sha1, char split_char)
{
/*	if(*source == 0){
		*word = 0;
		*sha1 = 0;
		return 0;
	}
	char *p = strrchr(source, split_char);
	int i=0;
	int split_char_pos = p - source;
	for(i = 0; i < split_char_pos; i++){
                *(word++) = *(source++);
	}
	*word='\0';
	source++;
        while(*source != '\n' && *source != EOF)
                *(sha1++) = *(source++);
	*sha1='\0';

        return 0;*/
}

int scomp(const void *p, const void *q )
{
	return strcmp( (char*) p, (char*) q );
}

int display_array(char ** array, int n)
{
	syslog(LOG_INFO, "----------begin dump-----------\n");
	int i=0;
	while (i<n && array[i] != NULL) {
		syslog(LOG_INFO, "%s\n", array[i]);
		i++;
	}
	syslog(LOG_INFO, "----------dump over------count: %d\n", i);
	return 0;
}

void init_g_result()
{
	int i=0;
	for (i=0; i<RESULTCOUNT; i++) 
		g_result[i] = NULL;
}

int binary_search (char *array[], int low, int high, char *key, int *count)
{
	if (low>=high) {
		return -1;
	} else {
		int mid = (low + high)/2;
		*count = *count + 1;
		int comp = scomp(key, array[mid]);
		if (comp = 0)
			return mid;
		else if (comp < 0) {
			return binary_search(array, low, mid-1, key, count);
		}
		else {
			return binary_search(array, mid+1, high, key, count);
		}
	}
}

int linear_search (char *array[], int size, char *key)
{
	int i=0;
	for (i = 0; i < size; i++)
		if (scomp(array[i], key) >=0)
			return i;
	return -1;
}

char ** lookup(char *key)
{
/*	int index = linear_search(g_titles, g_titles_count, key);
	g_result_index = index;
	int i = 0;
	while (i<RESULTCOUNT && g_titles[index] != NULL) {
		g_result[i] = malloc(MAXCHARS* sizeof(char));
		strcpy(g_result[i++], g_titles[index++]);
	}
	return g_result;*/
}

int search(char *fname)
{
	FIL file_object;
	char tmp[512];
	int n, total = 0;
	FRESULT result;
	SYSTIM begin_time;
	SYSTIM end_time;

	char *hash, *title;
	char line[LINECHARS];
	/* fgets(title,5,&file_object); */

	result = f_open(&file_object, fname, FA_READ);
	syslog(LOG_INFO, "f_open result = %d", result);
	if (result != 0)
		return -1;


	syslog(LOG_INFO, "benchmark search starting ...\n");
	result = f_read (&file_object, tmp, sizeof(tmp), &n);
	syslog(LOG_INFO, "f_read result = %d, n = %d", result, n);
	get_tim(&begin_time);
	do {
		result = f_read (&file_object, tmp, sizeof(tmp), &n);
		total += n;
/*		if (fgets(line, LINECHARS, &file_object) != NULL) {
		title = (char *) malloc(MAXCHARS * sizeof(char));
		hash = (char *) malloc(SHA1CHARS * sizeof(char));
		split(line, title, hash, '-');
		g_titles[g_titles_count] = title;
		g_hash[g_titles_count] = hash;
		syslog(LOG_INFO, "read lines: %d\n", g_titles_count++);
		}*/
	} while (result == 0 && n == sizeof(tmp));
	get_tim(&end_time);
	syslog(LOG_INFO, "time is :%d\n", end_time - begin_time);

/*	display_array(g_hash, g_titles_count);
	display_array(g_titles, g_titles_count);

	char c;
	syslog(LOG_INFO,"Enter title:");
	do {
	syscall(serial_rea_dat(TASK_PORTID, &c, 1));
	init_g_result();
	get_tim(&begin_time);

	lookup(title);
	get_tim(&end_time);
	syslog(LOG_INFO, "time is :%d\n", end_time - begin_time);

	int i = 0;
	while (g_titles[g_result_index] != NULL && i<RESULTCOUNT) {
	syslog(LOG_INFO, "%d\t%s---%s\n", i+1, g_titles[g_result_index], g_hash[g_result_index]);
	g_result_index++;
	i++;
	}
	syslog(LOG_INFO, "\nEnter title:");
	} while (c != '\003' && c!= 'Q');
*/
	syslog(LOG_INFO, "done.");
	return 0;
}

