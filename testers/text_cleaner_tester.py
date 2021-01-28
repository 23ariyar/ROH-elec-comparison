f = open('C:\\Users\\16507\\Documents\\Projects\\ROH-elec-comparison\\testers\\messy.txt')
words = f.read()


def text_cleaner(text):
        """
        Cleans text for images, filtered words, and non english words
        """
        #removes images and their captions
        '''
        while True:
            beg = text.find('![')
            end = text.find(')', beg)
            if beg != -1 and end != -1:
                text = text.replace(text[beg:end+1], '')
            else:
                break

        #removes non english words, do this when most of the words are removed, length process
        text = "".join(w for w in text if w.lower() in WORDS or not w.isalpha())

        #removes words in filter
        for word in FTR:
            text = text.replace(word, '')
         
        return text
        '''
        lines = text.split('\n')
        lines = ' '.join([line for line in lines if len(line.split()) >= 5])
        

        return lines

print(text_cleaner(words))