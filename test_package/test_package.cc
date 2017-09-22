#include <stdio.h>
#include <lqr.h>

int main()
{
	guchar *pixels = (guchar *)g_malloc(1);
	LqrCarver *carver = lqr_carver_new(pixels, 1, 1, 1);
	if (!carver)
	{
	    printf("Unable to initialize liblqr.\n");
		return -1;
	}

    printf("Successfully initialized liblqr.\n");

	lqr_carver_destroy(carver);

	return 0;
}
