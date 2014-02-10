import IMP
import IMP.core
import IMP.base
import IMP.algebra
import IMP.atom
import IMP.container

import IMP.pmi.restraints.stereochemistry as stereochemistry
import IMP.pmi.restraints.crosslinking as crosslinking
import IMP.pmi.representation as representation
import IMP.pmi.tools as tools
import IMP.pmi.samplers as samplers
import IMP.pmi.output as output

IMP.base.set_log_level(IMP.base.SILENT)



def check_time(stop_watch_object,threshold):
   elapsed_time=float(stop_watch_object.get_output()["Stopwatch_None_delta_seconds"])
   if (elapsed_time>threshold): print "WARNING: the calculation time of "+str(elapsed_time)+" is above the "+str(threshold)+" threshold"
   else:  print "the calculation time of "+str(elapsed_time)+" is below the threshold"

#input parameter

pdbfile="starting.structure.pdb"
fastafile="sequence.fasta"
fastids=tools.get_ids_from_fasta_file(fastafile)
missing_bead_size=1


#         Component  pdbfile    chainid  rgb color     fastafile     sequence id 
#                                                                    in fastafile
data = [("chainA",     pdbfile,   "A",     0.00000000,  (fastafile,    0)),
        ("chainB",     pdbfile,   "B",     0.50000000,  (fastafile,    0))]                    


#create the representation
log_objects=[]
optimizable_objects=[]

sw=tools.Stopwatch()
log_objects.append(sw)

m=IMP.Model()
r=representation.Representation(m) 

hierarchies={}

for d in data:
    component_name=d[0]
    pdb_file=d[1]
    chain_id=d[2]
    color_id=d[3]
    fasta_file=d[4][0]
    fasta_file_id=d[4][1]
    #avoid to add a component with the same name
    r.create_component(component_name,
                       color=color_id)
                       
    r.add_component_sequence(component_name,
                             fasta_file,
                             id=fastids[fasta_file_id])
                             
    hierarchies=r.autobuild_model(component_name,
                                   pdb_file,
                                   chain_id,
                                   resolutions=[1,10],
                                   missingbeadsize=missing_bead_size)
                                   
    r.show_component_table(component_name)

    
rbAB=r.set_rigid_bodies(["chainA","chainB"])

r.set_floppy_bodies()
r.fix_rigid_bodies([rbAB])
r.setup_bonds()


log_objects.append(r)

listofexcludedpairs=[]

lof=[(1,12,"chainA"),(1,12,"chainB"),
     (294,339,"chainA"),(294,339,"chainB"),
     (686,701,"chainA"),(686,701,"chainB"),
     (454,464,"chainA"),(454,464,"chainB"),     
     (472,486,"chainA"),(472,486,"chainB"),  
     (814,859,"chainA"),(814,859,"chainB")]



# add bonds and angles

for l in lof:

   rbr = IMP.pmi.restraints.stereochemistry.ResidueBondRestraint(r,l)
   rbr.add_to_model()
   listofexcludedpairs+=rbr.get_excluded_pairs()
   log_objects.append(rbr)

   rar = IMP.pmi.restraints.stereochemistry.ResidueAngleRestraint(r,l)
   rar.add_to_model()
   listofexcludedpairs+=rar.get_excluded_pairs()
   log_objects.append(rar)

# add excluded volume

ev = IMP.pmi.restraints.stereochemistry.ExcludedVolumeSphere(r,resolution=10.0)
ev.add_excluded_particle_pairs(listofexcludedpairs)
ev.add_to_model()
log_objects.append(ev)


mc = samplers.MonteCarlo(m,[r], 1.0)
log_objects.append(mc)

o = output.Output()

print "Starting test"
o.write_test("test.current.dict",log_objects)
o.test("test.IMP-2379ff1.PMI-348dcf70.dict",log_objects)

