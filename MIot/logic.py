# vcmx 文件中用于控制旋转塔和通信的代码
from vcScript import *
import random

app = getApplication()
comp = getComponent()
sim = getSimulation()

def OnSignal( signal ):
  global queue
  part = signal.Value
  part.stopMovement()
  queue.append(signal.Value)
def getAngles():
    angles = []
    for i in range(9):
        angle = comp.getProperty("Angle"+str(i))
        angles.append(angle.Value)
    return angles
def setupMTBF():
  global mtbf1,mtbf2,mtbf3
  mtbf1p = comp.getProperty('Process::MTBF1')
  mtbf2p = comp.getProperty('Process::MTBF2')
  mtbf3p = comp.getProperty('Process::MTBF3')
  if mtbf1p.Value > 0: mtbf1 = mtbf1p.Value * random.random()
  if mtbf2p.Value > 0: mtbf2 = mtbf2p.Value * random.random()
  if mtbf3p.Value > 0: mtbf3 = mtbf3p.Value * random.random()
  #repair_task = comp.getProperty('Process::RepairTask')

def checkMTBF():
  global mtbf1,mtbf2,mtbf3, stats
  mtbf1p = comp.getProperty('Process::MTBF1')
  mtbf2p = comp.getProperty('Process::MTBF2')
  mtbf3p = comp.getProperty('Process::MTBF3')
  mttr1p = comp.getProperty('Process::MTTR1')
  mttr2p = comp.getProperty('Process::MTTR2')
  mttr3p = comp.getProperty('Process::MTTR3')
  currentstate = stats.State
  if sim.SimTime > mtbf1 and mtbf1 > 0:
    stats.State = "Broken"
    delay(mttr1p.Value)
    v = mtbf1p.Value
    mtbf1 = sim.SimTime + v * (random.random() + 0.5)
  if sim.SimTime > mtbf2 and mtbf2 > 0:
    stats.State = "Broken"
    delay(mttr2p.Value)
    v = mtbf2p.Value
    mtbf2 = sim.SimTime + v * (random.random() + 0.5)
  if sim.SimTime > mtbf3 and mtbf3 > 0:
    stats.State = "Broken"
    delay(mttr3p.Value)
    v = mtbf3p.Value
    mtbf3 = sim.SimTime + v * (random.random() + 0.5)
  stats.State = currentstate

def OnRun():
  global queue,stats
  global mtbf1,mtbf2,mtbf3,previous_failure_fixed_at
  queue = []
  previous_failure_fixed_at = 0.0
  mtbf1 = 0
  mtbf2 = 0
  mtbf3 = 0
  servo = comp.findBehaviour("Servo Controller")
  out = comp.findBehaviour("OutputSlot__HIDE__")

  setupMTBF()
  stats = comp.findBehaviour("Statistics")
  output = comp.getProperty("Process::ProductionRate(PPM)")
  partsproduced = comp.getProperty("Statistics::PartsProduced")
  partsproduced.Value = 0
  defectrate = comp.getProperty("Process::DefectRate")
  defects = comp.getProperty("Statistics::Defects")
  defects.Value = 0
  OEEP = comp.getProperty("Statistics::OEEPerformance")
  OEEA = comp.getProperty("Statistics::OEEAvailability")
  OEEQ = comp.getProperty("Statistics::OEEQuality")
  OEE = comp.getProperty("Statistics::OEE")
  ppm = comp.getProperty("Statistics::ProductionRate(PPM)")
  
  servo.moveImmediate(0)
  for prop in servo.Properties:
    prop.IsVisible = False
  picks = {}
  drops = {}
  picks[0] = comp.findBehaviour("Tilt1__HIDE__")
  drops[-315] = comp.findBehaviour("Tilt1__HIDE__")
  picks[-315] = comp.findBehaviour("Tilt2__HIDE__")
  drops[-270] = comp.findBehaviour("Tilt2__HIDE__")
  picks[-270] = comp.findBehaviour("Tilt3__HIDE__")
  drops[-225] = comp.findBehaviour("Tilt3__HIDE__")
  picks[-225] = comp.findBehaviour("Tilt4__HIDE__")
  drops[-180] = comp.findBehaviour("Tilt4__HIDE__")
  picks[-180] = comp.findBehaviour("Tilt5__HIDE__")
  drops[-135] = comp.findBehaviour("Tilt5__HIDE__")
  picks[-135] = comp.findBehaviour("Tilt6__HIDE__")
  drops[-90] = comp.findBehaviour("Tilt6__HIDE__")
  picks[-90] = comp.findBehaviour("Tilt7__HIDE__")
  drops[-45] = comp.findBehaviour("Tilt7__HIDE__")
  picks[-45] = comp.findBehaviour("Tilt8__HIDE__")
  drops[-0] = comp.findBehaviour("Tilt8__HIDE__")
  vals = [0.0,0.0,0.0,90.0,180.0,180.0,90.0,0.0]
  #转盘角度和喷水夹具编号的映射
  spray = {}
  spray[0] = comp.findBehaviour("Tilt3__HIDE__")
  spray[-315] = comp.findBehaviour("Tilt4__HIDE__")
  spray[-270] = comp.findBehaviour("Tilt5__HIDE__")
  spray[-225] = comp.findBehaviour("Tilt6__HIDE__")
  spray[-180] = comp.findBehaviour("Tilt7__HIDE__")
  spray[-135] = comp.findBehaviour("Tilt8__HIDE__")
  spray[-90] = comp.findBehaviour("Tilt1__HIDE__")
  spray[-45] = comp.findBehaviour("Tilt2__HIDE__")
  sprayNo = {}
  sprayNo[0] = 3
  sprayNo[-315] = 4
  sprayNo[-270] = 5
  sprayNo[-225] = 6
  sprayNo[-180] = 7
  sprayNo[-135] = 8
  sprayNo[-90] = 1
  sprayNo[-45] = 2
  step = -45.0
  pick_and_drop = {}
  pick_and_drop[0] = (0,7)
  pick_and_drop[-315] = (1,0)
  pick_and_drop[-270] = (2,1)
  pick_and_drop[-225] = (3,2)
  pick_and_drop[-180] = (4,3)
  pick_and_drop[-135] = (5,4)
  pick_and_drop[-90] = (6,5)
  pick_and_drop[-45] = (7,6)
  stats.State = "Idle"
  warmuptime = -1
  Execute = comp.getProperty("WasherRun")
  move_start = comp.getProperty("StepStart")
  move_finish = comp.getProperty("StepFinish")
  Fixture = comp.getProperty("FixtureEnable")
  
  SprayEnable = comp.getProperty("SprayEnable")
  SpraySensor = comp.getProperty("SpraySensor")
  SprayNo = comp.getProperty("SprayNo")
  FixtureState = comp.getProperty("FixtureState")
  FixtureState.Value=0
  while True:
    
    #print "Execute: "%Execute.Value
    if not Execute.Value:
      delay(0.1)
      print "Sleep"
      continue
    angles_test = getAngles()
    delay(0.1)
    if move_start.Value:
      #print angles_test
      for i in range(9):
        servo.setJointTarget(i,angles_test[i])
      servo.setMotionTime(60.0 / output.Value)
      servo.move()
    val = servo.getJointValue(0)
    if val < -359.0: 
      angles_test[0] = 0
      for i in range(9):
        servo.setJointTarget(i,angles_test[i])
      servo.setMotionTime(0.0001)
      servo.move()
      val = 0
    
    
    checkMTBF()
    #Pick
    if queue and Fixture.Value and val in picks.keys():
      i =  pick_and_drop[val][0]
      if (FixtureState.Value & (2**i))==0:
        FixtureState.Value+=2**i
      part = queue.pop(0)
      container = picks[val]
      container.grab(part)
      stats.flowEnter(part)
      stats.State = "Busy"
    else:
      if len(comp.ChildComponents) == 0:
        stats.State = "Idle"
    #Spray
    if SprayEnable.Value and val in spray.keys():
      
      container = spray[val]
      if container.ComponentCount > 0:
        SpraySensor.Value = True
      SprayNo.Value = sprayNo[val]
    #Drop
    if val in drops.keys():
      currentstate = stats.State
      Block = comp.getProperty("Block")
      while out.ComponentCount > 0: 
        stats.State = "Blocked"
        Block.Value = True
        delay(0.5)
        #add stats
      Block.Value = False
      stats.State = currentstate
      container = drops[val]
      #Drop Movement
      if container.ComponentCount > 0:
        part = container.Components[0]
        partsproduced.Value +=1
        if random.random() < defectrate.Value:
          if part.getProperty("ProdID"): part.ProdID = "Defect"
          else:
            prodid = part.createProperty(VC_STRING,"ProdID")
            prodid.Value = "Defect"
          defects.Value +=1
        out.grab(part)
        i =  pick_and_drop[val][1]
        if (FixtureState.Value & (2**i))>0:
          FixtureState.Value-=2**i
        stats.flowLeave(part)
        part.startMovement()
    #Set finish signal until loop end
    if move_start.Value:
      move_finish.Value=True
###update machine statistics
    if partsproduced.Value > 0:
      if warmuptime == -1: 
        warmuptime = sim.SimTime-1.0
        stats.warmupCompleted()
      OEEP.Value = (stats.Utilization * ((partsproduced.Value-defects.Value)/ partsproduced.Value) * (((partsproduced.Value / sim.SimTime) * 60)/(output.Value)))/100.0
      OEEA.Value = (stats.BusyPercentage + stats.IdlePercentage) / 100.0
      OEEQ.Value = ((partsproduced.Value-defects.Value)/ partsproduced.Value)
      OEE.Value = OEEP.Value*OEEA.Value*OEEQ.Value
      ppm.Value = (partsproduced.Value / (sim.SimTime-warmuptime)) * 60