// STAR-CCM+ macro
// This runs a STAR-CCM+ job in parallel under a batch queing system
// CD-adapco
//=======================================
package macro;

import java.util.*;
import star.flow.*;
import star.common.*;
import star.base.neo.*;
import star.coremodule.services.*;
//import star.saturb.*;
//import star.keturb.*;
//import star.kwturb.*;
//import star.vof.*;
//import star.segregatedenergy.*;
//import star.segregatedflow.*;
//import star.segregatedspecies.*;
//import star.passivescalar.*;
//import star.coupledflow.*;

public class JOBNAME extends StarMacro {

  public void execute() {

    // Get the simulation in preparation for running
    Simulation simulation_0 = getActiveSimulation();


    // Set up iteration parameters
    SimulationIterator simulationIterator_0 = simulation_0.getSimulationIterator();

    simulationIterator_0.run(true);


  }
}