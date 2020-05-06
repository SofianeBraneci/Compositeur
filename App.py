# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 20:12:17 2019

@author: Braneci Sofiane
"""
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox as msgb
from graphv2 import * 
import matplotlib
from time import sleep
matplotlib.use('Agg')
matplotlib.pyplot.ioff()
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# main graph
G = None
# main graph with cs
G_with_cs = None
# discovery graph
U = None
# compostion graph
C = None
# best composition graph
B = None

class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Compositeur")
        self.geometry("685x650+200+50")
        self.resizable(0,0)
        self.menu = Menu(self)
        container = Frame(self)
        container.grid()
        self.frames = {}
        self.menu.add_command(label="Définition",
                              command=lambda: self._show_frame(DefinitionFrame))
        self.menu.add_command(label="Découverte",
                              command=lambda: self._show_frame(DiscoveryFrame))
        self.menu.add_command(label="Sélection",
                              command=lambda: self._show_frame(SelectionFrame))
        self.menu.add_command(label="Gestion QoS",
                              command=lambda: self._show_frame(GestionQoSFrameV2))
        self.menu.add_command(label="Composition",
                              command=lambda: self._show_frame(CompositionFrame))
        for F in (DefinitionFrame, DiscoveryFrame, GestionQoSFrameV2, SelectionFrame, CompositionFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nswe')
        self.configure(menu=self.menu)
        self._show_frame(DefinitionFrame)

    def _show_frame(self, f):
        frame = self.frames[f]
        frame.tkraise()
    def show_frame(self, f):
        frame = self.frames[f]
        frame.tkraise()
    def run(self):
        self.mainloop()

class DefinitionFrame(Frame):
    
    def __init__(self, parent, root):
        Frame.__init__(self, parent)
        self.parent = parent
        self.root_parent = root
        Label(self, text='Définition', font=('Lato', 20)).grid(row=0, column=0, padx=10, pady=10, sticky='W')
        container = Frame(self)
        container.grid(row=1, column=0, sticky="NW", columnspan=7)        
        Label(container, text=' nombre de  AS', font=('Lato', 10)).grid(row=0, column=0, sticky='W', padx=10)
        Label(container, text=' nombre de cs ', font=('Lato', 10)).grid(row=0, column=2, sticky='W', columnspan=2, padx=10)
        self.n_nodes_per_main_node = Entry(container, width=15)
        self.n_main_nodes = Entry(container, width=15)
        self.n_nodes_per_main_node.grid(row=0, column=5, padx=5, columnspan=2, sticky='W')
        self.n_main_nodes.grid(row=0, column=1, padx=5, sticky='W')
#        Label(self, text='Choisissez une structure', font=('Lato', 16)).grid(row=1, column=0, padx=10, pady=5, sticky='W')
#        self.cbx = Combobox(self, values=['Sequentielle','Parallèle','Boucle','Conditionnelle', 'Générer'])
#        self.cbx.grid(row=1, column=1, columnspan=2, sticky='W')
#        self.cbx.current(0)
        self.choice = IntVar(value=2)
        self.choice.set(1)
        Radiobutton(container, text='Graph sans cs', variable=self.choice, value=1).grid(row=1, column=0, padx=10)
        Radiobutton(container, text='Graph avec cs', variable=self.choice, value=2).grid(row=1, column=1, padx=10)
        Button(container, text="Afficher le graph", command= lambda : self.draw()).grid(row=1, column=3, padx=10, pady=5)
        Button(container, text='Générer', command = lambda : self.generate_graph()).grid(row = 0, column=7, padx=15, sticky='E')
        self.note_var = StringVar(value='')
        self.note = Label(self, textvariable=self.note_var)   
        self.note.grid(row=2, column=0, padx=10, pady=5, columnspan=4)
        
        
    def generate_graph(self):
        if float(self.n_main_nodes.get()) < 1.0 or float(self.n_nodes_per_main_node.get()) < 1.0 or not self.n_nodes_per_main_node.get().isdigit() or not self.n_main_nodes.get().isdigit() :
            msgb.showwarning('Attention', 'n AS et n cs  doivent être non null et positif')
            return
        global G
        global G_with_cs
        G = cgv5(int(float(self.n_main_nodes.get())))
        G_with_cs = construct_cs_graph(G, int(float(self.n_nodes_per_main_node.get())))

    def draw(self):
        if float(self.n_main_nodes.get()) < 1.0 or float(self.n_nodes_per_main_node.get()) < 1.0:
            msgb.showwarning('Attention', 'n AS et n cs  doivent être non null et positif')
            return
        if self.choice.get() == 1:
            fig = draw_definition_graph(G)
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.draw()
            self.graph_plot = canvas.get_tk_widget()
            if list(G.selfloop_edges()) != []:
                nodes = []
                for edge in list(G.selfloop_edges()):
                    if edge[0] not in nodes:
                        nodes.append(edge[0])
                self.note_var.set("Remarque: dans le(s) " + " ".join(nodes)+ "  le service concret qui sera séléction s'exécutera en boucle")
                self.note.grid(row=2, column=0, padx=10, pady=5, columnspan=5, sticky='W')
                self.graph_plot.grid(row=3, column=0, padx=10, pady=10, sticky='NSEW', columnspan=10)
            else:
                self.note.grid_forget()
                self.graph_plot.forget()
                self.graph_plot.grid(row=3, column=0, padx=50, pady=10, sticky='NSEW', columnspan=10)
        else:
            fig = draw_discovery_graph(G_with_cs)
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.draw()
            self.graph_plot = canvas.get_tk_widget()
            if list(G_with_cs.selfloop_edges()) != []:
                nodes = []
                for edge in list(G_with_cs.selfloop_edges()):
                    if edge[0] not in nodes:
                        nodes.append(edge[0])
                self.note_var.set("Remarque: dans le(s) " + " ".join(nodes)+ "  le service concret qui sera séléction s'exécutera en boucle")
                self.note.grid(row=2, column=0, padx=10, pady=5, columnspan=5, sticky='W')
                self.graph_plot.grid(row=3, column=0, padx=50, pady=10, sticky='NSEW', columnspan=10)
            else:
                self.note.grid_forget()
                self.graph_plot.forget()
                self.graph_plot.grid(row=3, column=0, padx=50, pady=10, sticky='NSEW', columnspan=10)

class DiscoveryFrame(Frame):
    def __init__(self, parent, root):
        Frame.__init__(self, parent)
        self.root_parent = root
        self.parent = parent
        Label(self, text='Découverte', font=('Lato', 20)).grid(row=0, column=0, padx=10, pady=5, sticky='W')
        Button(self, text='Générer le graph de découverte', command=lambda :self.on_generate()).grid(row=1, column=0, columnspan=4, padx=10, pady=4, sticky='NW')
        container = LabelFrame(self, text='Info sur les services chargé')
        container.grid(row=2, column=0, columnspan=4, sticky='WE', padx=10)
        vscroll = Scrollbar(container)
        hscroll = Scrollbar(container, orient=HORIZONTAL)
        vscroll.grid(row=0, column=1, sticky='NSW')
        hscroll.grid(row=2, column=0, sticky='SWE', padx=10)
        self.loaded_services =  Listbox(container, yscrollcommand=vscroll.set, width=67, height=5)
        self.loaded_services.grid(row=0, column=0, sticky='W', padx=10)
        vscroll.config(command=self.loaded_services.yview)
        self.graph_plot = None
        self.info = Listbox(container, width=67, height=2, xscrollcommand=hscroll.set)
        hscroll.config(command=self.info.xview)
        self.loaded_services.bind('<<ListboxSelect>>', self.on_select)
        self.info.grid(row=1, column=0, padx=10, sticky='W', pady=5)
    
    def on_generate(self):
        if G == None :
            msgb.showerror('Erreur', "Le graph de définition n'a pas était initialisé")
            self.root_parent.show_frame(DefinitionFrame)
            return
        else:
            global U
            U = construct_discovery_graph(G, get_n_cs(G_with_cs, G))
            self.get_services_data(U)
            self.render(U)
    
    def get_services_data(self, G):
        self.loaded_services.delete(0, END)
#        h = get_header()
#        h = f'{h[0]} {h[1]:>{30}} {h[2]:>{40}} {h[3]:>{30}} {h[4]:>{40}} {h[5]:>{30}} {h[6]:>{40}} {h[7]:>{30}} {h[8]:>{20}} {h[9]:>{25}} {h[10]:>{30}}'  
#        #self.loaded_services.insert(END, h)
        
        X = get_services_data(G)
        for x in range(len(X)):
            self.loaded_services.insert(END, '----- service dans AS '+str(x +1) + ' --------')
            for i in X[x]:
                self.loaded_services.insert(END, i[-1])
            self.loaded_services.insert(END, '---------------------------------')
    
    def on_select(self, event):
        self.info.delete(0, END)
        
        item = self.loaded_services.get(self.loaded_services.curselection())
        h = get_header()
        # h =  f'{h[0]} {h[1]:>{40}} {h[2]:>{40}} {h[3]:>{30}} {h[4]:>{40}} {h[5]:>{30}} {h[6]:>{40}} {h[7]:>{30}} {h[8]:>{20}} {h[9]:>{25}} {h[10]:>{30}}'
        h =  f'{h[0]} {h[1]:>{40}} {h[2]:>{40}}'
        
        self.info.insert(END, h)
        self.info.insert(END, self.format_output(get_item_data(item)))
        
    def format_output(self, h):
        return f'{h[0]} {h[1]:>{50}} {h[2]:>{50}}'          
    
    
    def render(self, U):
            fig = draw_discovery_graph(U)
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.draw()
            self.graph_plot = canvas.get_tk_widget()
            if self.graph_plot == None:
                self.graph_plot.grid(row=3, column=0, padx=10, pady=2, sticky='NSEW', columnspan=3)
            else:
                self.graph_plot.forget()
                self.graph_plot.grid(row=3, column=0, padx=10, pady=2, sticky='NSEW', columnspan=3)

class SelectionFrame(Frame):
    """
    TODO: change the way that the   Selector Object is created, this will be done 
    as soon as the other modules will be operating
    """
    def __init__(self, parent, root):
        Frame.__init__(self, parent)  
        self.root_parent = root
        Label(self, text='Sélection', font=('Lato', 20)).grid(row=0, column=0, padx=10, pady=10, sticky='W')
        container = LabelFrame(self, text='Préférences')
        container.grid(row=1, column=0, padx=80)
        
        Label(container, text='Response Time').grid(row=0, column=0)
        self.rt = Entry(container, width=10)
        self.rt.grid(row=0, column=1, padx=8)
           
        Label(container, text='Availability').grid(row=0, column=2)
        self.av = Entry(container, width=10)
        self.av.grid(row=0, column=3, padx=8)
#
#        Label(container, text='Throughput').grid(row=0, column=4)
#        self.th = Entry(container, width=10)
#        self.th.grid(row=0, column=5, padx=8)
#        
#        Label(container, text='Successability').grid(row=1, column=0, )
#        self.su = Entry(container, width=10)
#        self.su.grid(row=1, column=1, padx=8)
        
        Label(container, text='Reiability').grid(row=0, column=4,)
        self.rb = Entry(container, width=10)
        self.rb.grid(row=0, column=5, padx=8)
        
#        Label(container, text='Compliance').grid(row=1, column=4, pady=5)
#        self.cmp = Entry(container, width=10)
#        self.cmp.grid(row=1, column=5, padx=8, pady=5)
#        
#        Label(container, text='Best Practices').grid(row=2, column=0, padx=8, pady=5)
#        self.bp = Entry(container, width=10)
#        self.bp.grid(row=2, column=1, padx=8, pady=5)
#        
#        Label(container, text='Latency').grid(row=2, column=2, pady=5)
#        self.lt = Entry(container, width=10)
#        self.lt.grid(row=2, column=3, padx=8, pady=5)
#        
#        Label(container, text='Documentation').grid(row=2, column=4, pady=5)
#        self.doc = Entry(container, width=10)
#        self.doc.grid(row=2, column=5, padx=8, pady=5)
        Button(self, text='Sélectioner', command= lambda : self.on_select()).grid(row=3, column=0, padx=50, pady=5)
        self.note = Label(self, text='** La sélection peut prendre quelques instants **')
        self.note.grid(row=4, column=0, sticky='WS', padx=50, pady=10)
    def on_select(self):
        note = Label(self, text='Sélection terminé, aller vers la Gestion de QoS pour agréger le service composite', foreground = "green")
        note.forget()
        if G == None or U == None:
            msgb.showerror('Erreur', 'Le graph de définition n\'est pas initialité')
            self.root_parent.show_frame(DefinitionFrame)
        else:
            w = [self.rt.get(), self.av.get(),  self.rb.get()]
            global  C
            w = list(map(float, w))
            if any([True for i in range(len(w)) if w[i] >=1]):
                msgb.showwarning('Attention', 'Les valeurs des poids ne doivent pas dépasser 1')
            else:
                
                C = select(U, w, G)
                
                self.note.config(text='Sélection terminé, aller vers la Gestion de QoS pour agréger le service composite', foreground='green')
                # note.grid(row=4, column=0, padx=10, pady=10)
class GestionQoSFrame(Frame):
    
    def __init__(self, parent, root):
        self.root_parent = root
        Frame.__init__(self, parent)
        Label(self, text='Gestion QoS', font=('Lato', 20)).grid(row=0, column=0, padx=10, pady=10, sticky=W+N)
        
        Button(self, text='Agréger', command=lambda : self.on_agregate()).grid(row=2, column=0, padx=10, sticky=W+N, pady=20)
       
            
    def on_agregate(self):
        #seq_func, par_func, bou_func = self.get_func_names()
        if C == None:
            msgb.showerror('Erreur', 'Le graph de composition n\'a pas étais initialisé')
            self.root_parent.show_frame(SelectionFrame)
            return
        container1 = None
        X = get_header()
        r = evaluate_compositionv2(C)

        
#        container2 = LabelFrame(self, text='Parllèle', width=150)
#        container3 = LabelFrame(self, text='Boucle', width=150)
#        container4 = LabelFrame(self, text='Résultat de l\'agrégation du service composite', width=150)
        if container1 == None:
            container1 = LabelFrame(self, text='Résultat de l\'agrégation du service composite', width=150)
        
        else:
           container1.forget()
        container1 = LabelFrame(self, text='Résultat de l\'agrégation du service composite', width=150)
        container1.grid(row=3, column=0, sticky='SWN', padx=30, pady=50)
        Label(container1, text= X[0], font=('Lato', 12)).grid(row=0, column=0, padx=5, pady=10)
        Label(container1, text= str(r[0]), font=('Lato', 12)).grid(row=0, column=1, padx=20)
        
        Label(container1, text= X[1]+":", font=('Lato', 12)).grid(row=0, column=2, padx=5, pady=10)
        Label(container1, text= str(r[1]),font=('Lato', 12)).grid(row=0, column=3, padx=20)
        
        Label(container1, text= X[2]+":",font=('Lato', 12)).grid(row=0, column=4, padx=5, pady=10)
        Label(container1, text= str(r[2]), font=('Lato', 12)).grid(row=0, column=5, padx=20, pady=10)
        
        Label(container1, text= X[3]+":", font=('Lato', 12)).grid(row=1, column=0, padx=5)
        Label(container1, text= str(r[3]), font=('Lato', 12)).grid(row=1, column=1, padx=20, pady=10)
        
        Label(container1, text= X[4]+":", font=('Lato', 12)).grid(row=1, column=2, padx=5)
        Label(container1, text= str(r[4]), font=('Lato', 12)).grid(row=1, column=3, padx=20, pady=10)
        
        Label(container1, text= X[5]+":", font=('Lato', 12)).grid(row=1, column=4, padx=5)
        Label(container1, text= str(r[5]), font=('Lato', 12)).grid(row=1, column=5, padx=20, pady=10)
        
        Label(container1, text= X[6]+":", font=('Lato', 12)).grid(row=2, column=0, padx=5)
        Label(container1, text= str(r[6]), font=('Lato', 12)).grid(row=2, column=1, padx=20, pady=10)
        
        Label(container1, text= X[7]+":", font=('Lato', 12)).grid(row=2, column=2, padx=5)
        Label(container1, text= str(r[7]), font=('Lato', 12)).grid(row=2, column=3, padx=20, pady=10)
        
        Label(container1, text= X[8]+":", font=('Lato', 12)).grid(row=2, column=4, padx=5)
        Label(container1, text= str(r[8]), font=('Lato', 12)).grid(row=2, column=5, padx=20, pady=10 )
    
        
        
class GestionQoSFrameV2(Frame):
    
    def __init__(self, parent, root):
        self.root_parent = root
        Frame.__init__(self, parent)
        Label(self, text='Gestion QoS', font=('Lato', 20)).grid(row=0, column=0, padx=10, pady=10, sticky=W+N)
        
        Button(self, text='Agréger', command=lambda : self.on_agregate()).grid(row=2, column=0, padx=10, sticky=W+N, pady=20)
       
            
    def on_agregate(self):
        #seq_func, par_func, bou_func = self.get_func_names()
        if C == None:
            msgb.showerror('Erreur', 'Le graph de composition n\'a pas étais initialisé')
            self.root_parent.show_frame(SelectionFrame)
            return
        X = get_header()
        r = list(evaluate_compositionv3(C))
        print(E)
        
#        container1 = LabelFrame(self, text='Séquentielle', width=150)
#        container2 = LabelFrame(self, text='Parllèle', width=150)
#        container3 = LabelFrame(self, text='Boucle', width=150)
        container1 = LabelFrame(self, text='Résultat de l\'agrégation du service composite', width=150)

        
        
        # container1 = LabelFrame(self, text='Résultat de l\'agrégation du service composite', width=150)
        if r != []:
            container1.forget()
            container1.grid(row=3, column=0, sticky='SWN', padx=30, pady=30)
            Label(container1, text= X[0], font=('Lato', 12)).grid(row=0, column=0, padx=5, pady=10)
            Label(container1, text= str(r[0]), font=('Lato', 12)).grid(row=0, column=1, padx=20)
            
            Label(container1, text= X[1]+":", font=('Lato', 12)).grid(row=1, column=0, padx=5, pady=10)
            Label(container1, text= str(r[1]),font=('Lato', 12)).grid(row=1, column=1, padx=20)
            
            Label(container1, text= X[2]+":",font=('Lato', 12)).grid(row=2, column=0, padx=5, pady=10)
            Label(container1, text= str(r[2]), font=('Lato', 12)).grid(row=2, column=1, padx=20, pady=10)
            
#            Label(container1, text= X[3]+":", font=('Lato', 12)).grid(row=1, column=0, padx=5)
#            Label(container1, text= str(r[3]), font=('Lato', 12)).grid(row=1, column=1, padx=20, pady=10)
#            
#            Label(container1, text= X[4]+":", font=('Lato', 12)).grid(row=1, column=2, padx=5)
#            Label(container1, text= str(r[4]), font=('Lato', 12)).grid(row=1, column=3, padx=20, pady=10)
#            
#            Label(container1, text= X[5]+":", font=('Lato', 12)).grid(row=1, column=4, padx=5)
#            Label(container1, text= str(r[5]), font=('Lato', 12)).grid(row=1, column=5, padx=20, pady=10)
#            
#            Label(container1, text= X[6]+":", font=('Lato', 12)).grid(row=2, column=0, padx=5)
#            Label(container1, text= str(r[6]), font=('Lato', 12)).grid(row=2, column=1, padx=20, pady=10)
#            
#            Label(container1, text= X[7]+":", font=('Lato', 12)).grid(row=2, column=2, padx=5)
#            Label(container1, text= str(r[7]), font=('Lato', 12)).grid(row=2, column=3, padx=20, pady=10)
#            
#            Label(container1, text= X[8]+":", font=('Lato', 12)).grid(row=2, column=4, padx=5)
#            Label(container1, text= str(r[8]), font=('Lato', 12)).grid(row=2, column=5, padx=20, pady=10 )
        #########
#        container2.forget()
#        r = E[1]
#        if r != []:
#            container2.grid(row=4, column=0, sticky='SWN', padx=30, pady=7)
#            Label(container2, text= X[0], font=('Lato', 12)).grid(row=0, column=0, padx=5, pady=10)
#            Label(container2, text= str(r[0]), font=('Lato', 12)).grid(row=0, column=1, padx=20)
#            
#            Label(container2, text= X[1]+":", font=('Lato', 12)).grid(row=0, column=2, padx=5, pady=10)
#            Label(container2, text= str(r[1]),font=('Lato', 12)).grid(row=0, column=3, padx=20)
#            
#            Label(container2, text= X[2]+":",font=('Lato', 12)).grid(row=0, column=4, padx=5, pady=10)
#            Label(container2, text= str(r[2]), font=('Lato', 12)).grid(row=0, column=5, padx=20, pady=10)
            
#            Label(container2, text= X[3]+":", font=('Lato', 12)).grid(row=1, column=0, padx=5)
#            Label(container2, text= str(r[3]), font=('Lato', 12)).grid(row=1, column=1, padx=20, pady=10)
#            
#            Label(container2, text= X[4]+":", font=('Lato', 12)).grid(row=1, column=2, padx=5)
#            Label(container2, text= str(r[4]), font=('Lato', 12)).grid(row=1, column=3, padx=20, pady=10)
#            
#            Label(container2, text= X[5]+":", font=('Lato', 12)).grid(row=1, column=4, padx=5)
#            Label(container2, text= str(r[5]), font=('Lato', 12)).grid(row=1, column=5, padx=20, pady=10)
#            
#            Label(container2, text= X[6]+":", font=('Lato', 12)).grid(row=2, column=0, padx=5)
#            Label(container2, text= str(r[6]), font=('Lato', 12)).grid(row=2, column=1, padx=20, pady=10)
#            
#            Label(container2, text= X[7]+":", font=('Lato', 12)).grid(row=2, column=2, padx=5)
#            Label(container2, text= str(r[7]), font=('Lato', 12)).grid(row=2, column=3, padx=20, pady=10)
#            
#            Label(container2, text= X[8]+":", font=('Lato', 12)).grid(row=2, column=4, padx=5)
#            Label(container2, text= str(r[8]), font=('Lato', 12)).grid(row=2, column=5, padx=20, pady=10 )
#        else:
#            container2.destroy()
        
        #######
#        r = E[2]
#        if r != []:
#            container3.grid(row=5, column=0, sticky='SWN', padx=30, pady=7)
#            Label(container3, text= X[0], font=('Lato', 12)).grid(row=0, column=0, padx=5, pady=10)
#            Label(container3, text= str(r[0]), font=('Lato', 12)).grid(row=0, column=1, padx=20)
#            
#            Label(container3, text= X[1]+":", font=('Lato', 12)).grid(row=0, column=2, padx=5, pady=10)
#            Label(container3, text= str(r[1]),font=('Lato', 12)).grid(row=0, column=3, padx=20)
#            
#            Label(container3, text= X[2]+":",font=('Lato', 12)).grid(row=0, column=4, padx=5, pady=10)
#            Label(container3, text= str(r[2]), font=('Lato', 12)).grid(row=0, column=5, padx=20, pady=10)
#            
#            Label(container3, text= X[3]+":", font=('Lato', 12)).grid(row=1, column=0, padx=5)
#            Label(container3, text= str(r[3]), font=('Lato', 12)).grid(row=1, column=1, padx=20, pady=10)
#            
#            Label(container3, text= X[4]+":", font=('Lato', 12)).grid(row=1, column=2, padx=5)
#            Label(container3, text= str(r[4]), font=('Lato', 12)).grid(row=1, column=3, padx=20, pady=10)
#            
#            Label(container3, text= X[5]+":", font=('Lato', 12)).grid(row=1, column=4, padx=5)
#            Label(container3, text= str(r[5]), font=('Lato', 12)).grid(row=1, column=5, padx=20, pady=10)
#            
#            Label(container3, text= X[6]+":", font=('Lato', 12)).grid(row=2, column=0, padx=5)
#            Label(container3, text= str(r[6]), font=('Lato', 12)).grid(row=2, column=1, padx=20, pady=10)
#            
#            Label(container3, text= X[7]+":", font=('Lato', 12)).grid(row=2, column=2, padx=5)
#            Label(container3, text= str(r[7]), font=('Lato', 12)).grid(row=2, column=3, padx=20, pady=10)
#            
#            Label(container3, text= X[8]+":", font=('Lato', 12)).grid(row=2, column=4, padx=5)
#            Label(container3, text= str(r[8]), font=('Lato', 12)).grid(row=2, column=5, padx=20, pady=10 )
#            
#        else:
#            container3.destroy()
         
        
        


class CompositionFrame(Frame):
    def __init__(self, parent, root):
        Frame.__init__(self, parent)
        self.root_parent = root
        Label(self, text='Composition', font=('Lato', 20)).grid(sticky='NW',row=0, column=0, padx=10, pady=10)
        self.grah = None
        Button(self, text='Construire le Graphe de composition', command= lambda : self.construct() ).grid(sticky='W', row=1, column=0, columnspan=8, padx=10)
    
    def construct(self):
        if C == None:
            msgb.showerror("Erreur", "L'un (ou plusieurs) graph suivant n'est pas intialisé")
            if G == None:
                self.root_parent.show_frame(DefinitionFrame)
            elif U == None:
                self.root_parent.show_frame(DiscoveryFrame)
            else:
                self.root_parent.show_frame(SelectionFrame)
        else:
            fig = draw_definition_graph(C)
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.draw()
            self.graph = canvas.get_tk_widget()
            self.graph.grid(row=2, column=0, padx=10, pady=10)
       
#        self.max_iter = Entry(self, width=10)
#        Button(self, text='Générer le graph de composition optimal', command=lambda :self.construct_best()).grid(row=3, column=0, padx=10, pady=5, sticky=W)
#        Label(self, text='nombre d\'iteration').grid(row=3, column=1, padx=10, sticky=W)
#        self.max_iter.grid(row=3, column=2, padx=10, pady=5, sticky=W)
#    def construct_best(self):
#        global B
#        if int(self.max_iter.get()) <= 0:
#            msgb.showwarning('Attention', 'Max iteration doit être non null et positif')
#        else:
#            B = get_best_composition(C, int(self.max_iter.get()))
#            self.graph.forget()
#            fig = draw_definition_graph(B)
#            canvas = FigureCanvasTkAgg(fig, self)
#            canvas.draw()
#            self.graph = canvas.get_tk_widget()
#            self.graph.grid(row=2, column=0, padx=80, pady=10)
        
        
        
            
if __name__ == '__main__':
    App().run()
    