givenstring="Lorem ipsum dolor! diam amet, consetetur Lorem magna. sed diam nonumy eirmod tempor. diam et labore? et diam magna. et diam amet."
class textAnalyzer:
    def __init__(self,text):
        newtext=text.lower()
        newtext=newtext.replace("!"," ").replace(","," ").replace("."," ").replace("?"," ")
        self.text=newtext
        def freqAll(self):
            word=self.text.split()    
        def createDict(self):
            dict={}
            for keys in word:
               dict[keys]=word.count(keys)  
            return dict  
          

# class TextAnalyzer(object):
    
#     def __init__ (self, text):
#         # remove punctuation
#         formattedText = text.replace('.','').replace('!','').replace('?','').replace(',','')
        
#         # make text lowercase
#         formattedText = formattedText.lower()
        
#         self.fmtText = formattedText
        
#     def freqAll(self):        
#         # split text into words
#         wordList = self.fmtText.split(' ')
        
#         # Create dictionary
#         freqMap = {}
#         for word in set(wordList): # use set to remove duplicates in list
#             freqMap[word] = wordList.count(word)
        
#         return freqMap