from Tkinter import *           #Importaion Of Modules
from bs4 import BeautifulSoup
import urllib2
from docclass import *

class FacultyMember:        #Creating Faculty members class with appropriate attributes
    def __init__(self, name, profile_url, publications):
        self.name = name
        self.profile_url = profile_url
        self.publications = publications

class ResearchProject:      #Creating research class with appropriate attributes
    def __init__(self, title, summary, PI_name):
        self.title = title
        self.summary = summary
        self.PI_name = PI_name




class Predictor:            #Creating Predictor class with appropriate attributes
    def __init__(self, classifier, faculty_members, projects):
        self.classifier = classifier
        self.faculty_members = faculty_members
        self.projects = projects


    def fetch_members(self, url):  #This method will parse the first link and get the names
        response = urllib2.urlopen(url)
        html_doc = response.read()      #opening link
        soup = BeautifulSoup(html_doc, 'html.parser')
        for link in soup.find_all('a'):     #parsing for all a in html code
            if str(link.get('href')).startswith('/en/profile'):     #if the a link is a profile
                profile_url = 'http://cs.sehir.edu.tr' + link.get('href')   #accessing profile
                opening = urllib2.urlopen(profile_url)
                html_document = opening.read()
                page = BeautifulSoup(html_document, 'html.parser')
                #adding to members dictionary only the first and last name
                self.faculty_members[page.title.text.split('\n')[0].strip(' ').split(' ')[0] + ' ' + page.title.text.split('\n')[0].strip(' ').split(' ')[-1]] = FacultyMember(page.title.text.split('\n')[0].strip(' ').split(' ')[0] + ' ' + page.title.text.split('\n')[0].strip(' ').split(' ')[-1], profile_url, [])
                self.fetch_publications(page)   #calling function that will get the publications of each profile

    def fetch_publications(self,page):
        for ul in page.find_all('div',class_ = 'tab-pane active pubs'): #searching for all ul in web page code
            for li in ul.find_all('li'):    #searching for li elements in ul
                #if the publiction is not found in the list it appends it
                if li.text.strip().split('. \n')[1].splitlines()[0] not in self.faculty_members[page.title.text.split('\n')[0].strip(' ').split(' ')[0] + ' ' + page.title.text.split('\n')[0].strip(' ').split(' ')[-1]].publications:
                    self.faculty_members[page.title.text.split('\n')[0].strip(' ').split(' ')[0] + ' ' + page.title.text.split('\n')[0].strip(' ').split(' ')[-1]].publications.append(li.text.strip().split('. \n')[1].splitlines()[0])



    def fetch_projects(self,url):       #function that parses second link
        response = urllib2.urlopen(url) #opening second link
        html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        for li in soup.find_all('ul', {'class':'list-group'}):  #searching for all ul code with class = list-group """this was learned from stackoverflow"""
            for content in li.find_all('li', {'class':'list-group-item'}): #searching for all li with class list-group-item in ul
                if content.text.strip().splitlines()[16].strip() in self.faculty_members:   #if the pi name is in the current faculty members
                    summary = (" ".join(content.text.strip().splitlines()[22:]))    #extracting summary from list of several general content
                    #adding to projects dictionary
                    self.projects[content.text.strip().splitlines()[0]] = ResearchProject(content.text.strip().splitlines()[0],summary,content.text.strip().splitlines()[16].strip())
        self.train_classifier() #calling the method to train the classifier attribute


    def train_classifier(self):
        for name in self.faculty_members: #training the classifier with the first object being a documnet and the name being the category
            for publication in self.faculty_members[name].publications: self.classifier.train(publication,name)

    def predict_PI(self,selection): #function that will predict name
        for project in self.projects:
            if selection == project:    #if the listbox selesction equals name
                #if prediction is correct it returns a list with color and name
                if self.classifier.classify(self.projects[project].title+self.projects[project].summary) == self.projects[project].PI_name: return ['green',self.projects[project].PI_name]
                else: #if prediction is incorect returns the predicted name and the color red
                    return ['red',self.classifier.classify(self.projects[project].title+self.projects[project].summary)]


class GUI(Frame):   #class that display GUI
    def __init__(self, parent):
        self.parent = parent
        Frame.__init__(self, parent)
        self.initUI(parent)
        self.predictor = Predictor(naivebayes(getwords),{},{})  #creating object for predictor class as attribute of class

    def initUI(self, parent):   #method to create gui
        Label(self, text='PI Estimator Tool For SEHIR CS Projects', font=("Helvetica", 20, "bold"), bg='#00a0af', fg='White', width=55).grid(row=0, column=0, sticky=W)
        self.url1 = Entry(self,justify = 'center')
        self.url1.grid(row=1, padx=152, sticky=W, pady=17, ipadx=270)
        self.url1.insert(END, 'http://cs.sehir.edu.tr/en/people/')
        self.url2 = Entry(self,justify = 'center')
        self.url2.grid(row=2, padx=152, sticky=W, ipadx=270)
        self.url2.insert(END, 'http://cs.sehir.edu.tr/en/research/')
        self.button = Button(self, text='Fetch', font=('Helvetica',10,'bold'), command=self.fetching)
        self.button.grid(row=3, ipadx=19, pady=10, sticky=W, padx=440)
        Label(self, text='Projects', font=('Helvetica', 16)).grid(row=4, sticky=W, padx=350)
        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.listbox1 = Listbox(self, yscrollcommand=self.scrollbar.set)
        self.listbox1.grid(row=5, sticky=W, padx=100, ipadx=220)
        self.scrollbar.config(command=self.listbox1.yview)
        self.scrollbar.grid(row=5, sticky=W, padx=665, pady=5, ipady=56)
        self.listbox1.bind('<<ListboxSelect>>',self.display_prediction)  # binding the selection of any element in the listbox to call a method
        Label(self, text='Prediction', font=('Helvetica',16)).grid(row=4, sticky=W, padx=730)
        self.prediction = Label(self)
        self.prediction.grid(row=5, sticky=W, padx=720)
        self.pack()
    def fetching(self): #pressing to fetch buttons calls this method
        self.listbox1.delete(0,END)
        self.predictor.fetch_members(self.url1.get())   #argument is link in the entry
        self.update_idletasks() #to make the code run a little faster """according to my personal observations"""
        self.predictor.fetch_projects(self.url2.get())
        for i in sorted(self.predictor.projects.keys()): #getting only the keys of the dictionary as a list and sorting it alphabetically
            self.listbox1.insert(END,i) #inserting list into listbox
    def display_prediction(self,none):#function that will call prediction method from predictor class and display the prediction
        #the second argument isnt used, it was added because otherwise an error would appear,
        #after researching a little we can access a widget attribute for the second item and also use that to get selection but i find this way simpler

        answer = self.predictor.predict_PI(self.listbox1.get(self.listbox1.curselection()))
        self.update_idletasks()
        if answer[0] == 'green': self.prediction.configure(text = answer[1],bg = 'green',font = ('Helvetica',20))
        else: self.prediction.configure(text = answer[1],bg = 'red',font = ('Helvetica',20))




def main():  # function that runs the app by creating object of tk and GUI class which takes the object of tk as argument
    root = Tk()
    root.geometry('935x400')
    root.title('PI Estimator Tool For SEHIR CS Projects')
    app = GUI(root)
    root.mainloop()
main()





