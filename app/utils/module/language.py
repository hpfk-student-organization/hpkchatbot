"""

This module provides access to different types of sorted alphabets

"""

UA = ('А', 'Б', 'В', 'Г', 'Ґ', 'Д', 'Е', 'Є', 'Ж', 'З', 'И', 'І', 'Ї', 'Й', 'К', 'Л', 'М', 'Н',
      'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ь', 'Ю', 'Я')

RU = ('А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Ї', 'Й', 'К', 'Л', 'М', 'Н',
      'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я')

EN = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
      'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')

UA_RUS = ('А', 'Б', 'В', 'Г', 'Ґ', 'Д', 'Е', 'Є', 'Ё', 'Ж', 'З', 'И', 'І', 'Ї', 'Й', 'К', 'Л', 'М', 'Н',
          'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я')

NUMERAL = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')

UA_NUM = (*UA, *NUMERAL)
RU_NUM = (*RU, *NUMERAL)
EN_NUM = (*EN, *NUMERAL)

UA_RUS_NUM = (*UA_RUS, *NUMERAL)

UA_RUS_EN = ('А', 'A', 'Б', 'В', 'B', 'Г', 'Ґ', 'Д', 'Е', 'E', 'Ё', 'Є', 'Ж', 'З', 'И', 'І', 'I', 'Ї', 'Й', 'К',
             'K', 'Л', 'М', 'M', 'Н', 'H', 'О', 'O', 'П', 'Р', 'Р', 'С', 'C', 'Т', 'T', 'У', 'Ф', 'Х', 'X', 'Ц',
             'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я', 'D', 'F', 'G', 'J', 'L', 'N', 'Q', 'R', 'S', 'U', 'V',
             'W', 'Y', 'Z')

COMBO_UA_RUS_EN__NUM = (*UA_RUS_EN, *NUMERAL)
