import glob
import re
from math import exp, pow

R = 0.001987207  # kcal/mol*K
T = 298.15  # K


class Result_Analysis():
    def __init__(self, prog=None, mol=None, ligand=None):
        self.prog = prog
        self.mol = mol
        self.ligand = ligand
        self.result2pdb()

    def energy2ki(self, energy):
        energy = float(energy)
        Ki = exp(energy / (R * T))
        return Ki

    def converter(self, number):
        units = ['M', 'mM', 'uM', 'nM']
        exponente = 0
        base = pow(10, exponente)
        out_number = number * base
        while out_number < 1 or out_number > 10:
            exponente += 1
            base = pow(10, exponente)
            out_number = number * base
        if exponente in [0, 1]:
            rep_number = number
            return rep_number, units[0]
        elif exponente in [2, 3, 4]:
            rep_number = number * 1000
            return rep_number, units[1]
        elif exponente in [5, 6]:
            rep_number = number * 1000000
            return rep_number, units[2]
        elif exponente in [7, 8, 9, 10]:
            rep_number = number * 1000000000
            return rep_number, units[3]
        else:
            rep_number = number
            return rep_number, '-'

    def result2table(self, p_file, score=False):
        file = open(p_file, 'r')
        modes = []
        pose = 1
        energy = 0

        for line in file:
            line = line.strip("\n")
            if score:
                if re.search('Affinity:', line):
                    energy = float(line.split()[1])
                    break
                elif re.search('Estimated Free Energy of Binding', line):
                    energy = float(line.split()[8])
                    break
            else:
                if re.search('REMARK ENERGY', line):
                    energy = float((line.split()[3]).strip())
                    if energy:
                        Ki_value = self.energy2ki(energy)
                        Ki, unit = self.converter(Ki_value)
                        ligand_efficiency = energy / self.ligand.ha
                        modes_info = [pose, energy, '%.2f' % Ki, unit, '%.2f' % ligand_efficiency]
                        modes.append(modes_info)
                        pose += 1
        if score and energy:
            Ki_value = self.energy2ki(energy)
            Ki, unit = self.converter(Ki_value)
            ligand_efficiency = energy / self.ligand.ha
            modes_info = [pose, energy, '%.2f' % Ki, unit, '%.2f' % ligand_efficiency]
            modes.append(modes_info)
        # improve blind docking output
        modes.sort(key=lambda x: x[1])
        return modes

    def result2pdb(self):
        # check if exist docking result
        if self.prog == 'AutoDock Vina':
            if len(glob.glob('%s_%s_out*.pdbqt' % (self.ligand.pdbqt_name, self.mol.name))) >= 1:
                self.rfiles = glob.glob('%s_%s_out*.pdbqt' % (self.ligand.pdbqt_name, self.mol.name))
            else:
                return
        else:
            if len(glob.glob('%s_%s_out*.dlg' % (self.ligand.pdbqt_name, self.mol.name))) >= 1:
                self.rfiles = glob.glob('%s_%s_out*.dlg' % (self.ligand.pdbqt_name, self.mol.name))
            else:
                return

        output_file = open(self.mol.all_poses, 'w')
        models = 1
        output_file.write('REMARK Generated by AMDock from %s result\n' % self.prog)
        if len(self.rfiles) > 1:
            output_file.write('REMARK Best docking result from each FILL generated by AutoLigand' + '\n')
        for ffill in self.rfiles:
            result = open(ffill, 'r')
            for line in result:
                line = line.strip('\n')
                if self.prog == 'AutoDock Vina':
                    if re.search('MODEL', line[:5]):
                        output_file.write('MODEL' + ('%d' % models).rjust(9) + '\n')
                        ofile = open('%s_%s_out%02d.pdb' % (self.ligand.name, self.mol.name, models), 'w')
                        ofile.write('REMARK Generated by AMDock from %s result\n' % self.prog)
                        if len(self.rfiles) > 1:
                            output_file.write('REMARK Best docking result from each FILL generated by AutoLigand' +
                                              '\n')
                        ofile.write('MODEL' + ('%d' % models).rjust(9) + '\n')
                        models += 1
                    elif re.search('ATOM', line[:5]) or re.search('HETATM', line[:6]):
                        output_file.write('HETATM' + line[7:67] + line[13:14].rjust(11) + '\n')
                        ofile.write('HETATM' + line[7:67] + line[13:14].rjust(11) + '\n')
                    elif re.search('ENDMDL', line[:6]):
                        output_file.write(line + '\n')
                        ofile.write(line + '\n')
                        ofile.close()
                    if re.search('REMARK VINA RESULT', line):
                        output_file.write('REMARK ENERGY   =   %s\n' % line.split()[3].strip())
                        ofile.write('REMARK ENERGY   =   %s\n' % line.split()[3].strip())
                else:
                    if re.search('MODEL', line[:5]):
                        output_file.write('MODEL' + ('%d' % models).rjust(9) + '\n')
                        ofile = open('%s_%s_out%02d.pdb' % (self.ligand.name, self.mol.name, models), 'w')
                        ofile.write('REMARK Generated by AMDock from %s result\n' % self.prog)
                        if len(self.rfiles) > 1:
                            output_file.write('REMARK Best docking result from each FILL generated by AutoLigand' +
                                              '\n')
                        ofile.write('MODEL' + ('%d' % models).rjust(9) + '\n')
                        models += 1
                    elif re.search('ATOM', line[:5]) or re.search('HETATM', line[:6]):
                        output_file.write('HETATM' + line[7:67] + line[12:14].rjust(11) + '\n')
                        ofile.write('HETATM' + line[7:67] + line[12:14].rjust(11) + '\n')
                    elif re.search('ENDMDL', line[:6]):
                        output_file.write(line + '\n')
                        ofile.write(line + '\n')
                        ofile.close()
                        if len(self.rfiles) > 1 and models == 2:
                            break
                    if re.search('USER {4}Estimated Free Energy of Binding', line[:43]):
                        output_file.write('REMARK ENERGY   =   %s\n' % line.split()[7].strip())
                        ofile.write('REMARK ENERGY   =   %s\n' % line.split()[7].strip())
            result.close()
        output_file.close()
