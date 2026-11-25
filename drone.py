#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 11:25:56 2026

@author: christophersaab
"""
import matplotlib.pyplot as plt
import random as rand

def load_map(filename):
    try:
        file=open(filename,"r")
        lines=file.readlines()
        file.close()
        grid=[]
        places={}
        for i in range(len(lines)):
            grid.append(list(lines[i].strip()))
            for j in range(len(grid[i])):
                if grid[i][j]!="#" and grid [i][j]!=".":
                    places[grid[i][j]]=[i,j]
            
        return grid,places
    except FileNotFoundError:
        print("File not Found")
        return None,None


class Drone(object):
    
    def __init__(self,name,start,battery):
        assert type(name)==str and type(start)==list and len(start)==2 and type(battery)==int and battery>=0,"Bad Input!"
        self.name=name
        self.pos=start.copy()
        self.battery=battery
        self.log=[start.copy()]
    def __str__(self):
        return (self.name)+" at "+str(self.pos)+", battery "+str(self.battery)
    def cost(self):
        return 1
    def move_to(self,r,c):
       dr=r-self.pos[0]
       dc=c-self.pos[1]
       assert (abs(dr)+abs(dc))==1,"Bad Move!"
       if self.battery<=0:
           self.battery=0
           return False
       self.pos=[r,c]
       self.battery-=self.cost()
       self.log.append(self.pos.copy())
       return True
    
    def fly(self,path):
        for i in range(1,len(path)):
            if not self.move_to(path[i][0],path[i][1]):
                
                return False
        return True

class CargoDrone(Drone):
    def __init__(self, name, start, battery):
        Drone.__init__(self, name, start, battery)
        self.packages=[]
        
    def load(self,letter):
        assert type(letter)==str,"Bad Input!"
        self.packages.append(letter)
    def deliver(self):
        assert len(self.packages)>0, "No packages!"
        return self.packages.pop()
        
    def __str__(self):
        return Drone.__str__(self)+", packages "+str(self.packages)
    def cost(self):
        if len(self.packages)>=2:
            return 2
        return 1

def new_visited(grid):
    return [[False for x in range(len(grid[i]))]for i in range(len(grid))]
def find_path(grid,r,c,target,visited):
    
    if grid[r][c]=="#":
        return None
    if visited[r][c]:
        return None
    if target==[r,c]:
        return [[r,c]]
    visited[r][c]=True
    if not visited[r-1][c]:
        p=find_path(grid, r-1, c, target, visited)
        if p!=None:
            return [[r,c]]+p
    if not visited[r+1][c]:
        p=find_path(grid, r+1, c, target, visited)
        if p!=None:
             return [[r,c]]+p
    if not visited[r][c-1] :
        p=find_path(grid, r, c-1, target, visited)
        if p!=None:
            return [[r,c]]+p
    if not visited[r][c+1]:
        p=find_path(grid, r, c+1, target, visited)
        if p!=None:
            return [[r,c]]+p
   
def check_path(grid,path,start,end):
    if path==None or len(path)==0:
        return False
    
    if path[0]!=start or path[-1]!=end:
        return False
    if grid[path[0][0]][path[0][1]]=="#":
        return False
   
    for i in range(1,len(path)):
        if abs(path[i][0]-path[i-1][0])+abs(path[i][1]-path[i-1][1])!=1:
            return False
        if grid[path[i][0]][path[i][1]]=="#":
            return False
    return True
        
      

def distances(grid,places):
    D={}
    for letter in places:
        if letter!="S":
            p=find_path(grid,places["S"][0], places["S"][1], places[letter], new_visited(grid))
            if p==None:
                print(D[letter]," is unreachable")
            else:
                D[letter]=len(p)-1
        
    return D

def randompartition(L,p,r):
    
    u=rand.randint(p,r)
    (L[u],L[r])=(L[r],L[u])
    i=p-1
    x=L[r]
    for j in range(p,r):
        if L[j]<x:
            i+=1
            (L[i],L[j])=(L[j],L[i])
    (L[i+1],L[r])=(L[r],L[i+1])
    q=i+1
    return q
def quicksort(L):
    p=0
    r=len(L)-1
    return helper(L,p,r)
def helper(L,p,r):
    if p<r:
        q=randompartition(L, p, r)
        helper(L,p,q-1)
        helper(L,q+1,r)
    return L
        
def delivery_order(D):
    L=[]
    l=[]
    for i in D:
        L.append([D[i],i])
    for i in quicksort(L):
        l.append(i[1])
    return l
        
def fly_mission(grid,places,battery,verbose=True,p=0):
    delorder=delivery_order(distances(grid, places))
    cargo=WindyCargoDrone("Cargo", places["S"], battery,p)
   
    delorder.reverse()
    for i in delorder:
        cargo.load(i)
    delorder.reverse()  
    if verbose:
        print(cargo)
    for target in delorder:
        start=cargo.pos
        r=find_path(grid, start[0],start[1],places[target], new_visited(grid))
        if check_path(grid, r, start,places[target]):
            if not cargo.fly(r):
                if verbose:
                    print("Battery died at ",cargo.pos)
                return False
            delivered=cargo.deliver()
            assert delivered==target
            if verbose:
                print(cargo)
        else:
            if verbose:
                print("Invalid route")
            return False
       
    return True


class WindyCargoDrone(CargoDrone):
    def __init__(self,name,start,battery,p):
        CargoDrone.__init__(self,name,start,battery)
        self.p=p
    def move_to(self,r,c):
        
         if CargoDrone.move_to(self,r,c):
             
             if rand.random()<self.p:
                 
                 self.battery-=1
                 if self.battery<=0:
                     self.battery=0
                 
             return True
         return False
             

def monteCarloplotting(n=1000):
    X=[x for x in range(60,88,2)]
    grid,places=load_map("map.txt")
    successrate=[]
    for i in X:
        success=0
        
        for j in range(n):
            if fly_mission(grid, places,i,False,0.3):
                success+=1
        successrate.append(100*success/n)
    plt.title("Mission success vs starting battery (wind p=0.3)")
    plt.plot(X,successrate,"r")
    plt.xlabel("Starting battery")
    plt.ylabel("Success rate %")
    
    plt.show()
    return X,successrate
    
            
    
# ================= tests =================

def banner(title):
    print()
    print("=" * 10, title, "=" * 10)

def test_stage1():
    banner("STAGE 1: load_map")
    grid, places = load_map("map.txt")
    print("rows, cols:", len(grid), len(grid[0]))       # 9 10
    print("row 1:", grid[1])                            # ['#', 'S', '.', '.', '.', '#', '.', '.', '.', '#']
    print("places:", places)                            # {'S': [1, 1], 'A': [3, 8], 'B': [5, 4], 'C': [7, 1]}
    print("bad file:", load_map("mapp.txt"))            # File not Found / (None, None)

def test_stage2():
    banner("STAGE 2: Drone")
    d = Drone("D1", [1, 1], 2)
    print(d.move_to(2, 1), d)                           # True D1 at [2, 1], battery 1
    print(d.move_to(3, 1), d)                           # True D1 at [3, 1], battery 0
    print(d.move_to(4, 1), d)                           # False D1 at [3, 1], battery 0
    print("log:", d.log)                                # [[1, 1], [2, 1], [3, 1]]

    banner("STAGE 2: fly")
    path = [[1, 1], [2, 1], [3, 1], [4, 1], [5, 1]]
    print("full battery:", Drone("F1", [1, 1], 10).fly(path))     # True
    print("runs out:", Drone("F2", [1, 1], 2).fly(path))          # False

    banner("STAGE 2: CargoDrone")
    c = CargoDrone("C1", [1, 1], 10)
    c.load("B")
    c.load("A")
    print(c, "| cost:", c.cost())                       # ... packages ['B', 'A'] | cost: 2
    print("delivered:", c.deliver(), "| cost:", c.cost())   # A | cost: 1

def test_stage3():
    banner("STAGE 3: find_path + check_path")
    grid, places = load_map("map.txt")
    S = places["S"]
    for letter in ["A", "B", "C"]:
        route = find_path(grid, S[0], S[1], places[letter], new_visited(grid))
        print(letter, "moves:", len(route) - 1, "valid:", check_path(grid, route, S, places[letter]))
        # A 17 True / B 27 True / C 10 True
    print("to a wall:", find_path(grid, 1, 1, [0, 0], new_visited(grid)))     # None
    print("gap:", check_path(grid, [[1, 1], [1, 2], [1, 4]], [1, 1], [1, 4]))  # False
    print("no path:", check_path(grid, None, S, [0, 0]))                        # False

def test_stage4():
    banner("STAGE 4: planning")
    grid, places = load_map("map.txt")
    dist = distances(grid, places)
    print("distances:", dist)                           # {'A': 17, 'B': 27, 'C': 10}
    print("order:", delivery_order(dist))               # ['C', 'A', 'B']

    banner("STAGE 4: mission, battery 60")
    print(fly_mission(grid, places, 60))                # 4 drone lines, then True
    banner("STAGE 4: mission, battery 59")
    print(fly_mission(grid, places, 59))                # dies at [5, 5], then False

def test_stage5():
    banner("STAGE 5: WindyCargoDrone")
    path = [[1, 1], [2, 1], [3, 1], [4, 1], [5, 1]]
    w0 = WindyCargoDrone("W0", [1, 1], 10, 0)
    w0.load("X")
    w0.load("Y")
    print("p=0:", w0.fly(path), w0)                     # True W0 at [5, 1], battery 2, ...
    w1 = WindyCargoDrone("W1", [1, 1], 12, 1)
    w1.load("X")
    w1.load("Y")
    print("p=1:", w1.fly(path), w1)                     # True W1 at [5, 1], battery 0, ...

    banner("STAGE 5: windy mission")
    grid, places = load_map("map.txt")
    print("p=0, 60:", fly_mission(grid, places, 60, False, 0))    # True
    print("p=0, 59:", fly_mission(grid, places, 59, False, 0))    # False
    print("p=1, 80:", fly_mission(grid, places, 80, False, 1))    # False
    print("p=1, 95:", fly_mission(grid, places, 95, False, 1))    # True

    banner("STAGE 5: Monte Carlo (p=0.3, 1000 runs)")
    X, rates = monteCarloplotting(1000)
    for i in range(len(X)):
        print("battery", X[i], ":", rates[i], "%")
    # roughly: 62→0, 66→8, 68→27, 70→55, 72→82, 74→94, 76→99, 78+→100
    # (Monte Carlo varies by a few % each run)

# ---- run ----
test_stage1()
test_stage2()
test_stage3()
test_stage4()
test_stage5()