from params import *
import platform
import time
import numpy as np
import os
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

parser = ArgumentParser()
parser.add_argument('--input_file', default='./CSA_120_days/Indianapolis_Carmel_Muncie, IN_day47.csv')
args = parser.parse_args()

BOUNDS={
    'kappa':[0,20],
    'C_0':[1,2000],
    'I_0':[1,1000],
    'P_suc':[0,2],
    'SocDist_on':[0,100],
    'SocDist_init':[0,1],
    'SocDist_fnl':[0,1],
    'SocDist_switch':[0,100],
    'SocRel_on':[0,750],
    'SocRel_init':[0,1],
    'SocRel_fnl':[0,5],
    'SocRel_switch':[0,350],
    'Surveil_on':[0,100],
    'Surveil_init':[0,0.5],
    'Surveil_fnl':[0,1],
    'Surveil_switch':[0,1000]
    }

os.linesep='\n'

class CSA:
    def __init__(self):
        self.data = np.genfromtxt(args.input_file, delimiter=',').astype(np.int)
        print('Total days in data: {}'.format(self.data.shape[1]))
        assert self.data.shape[1] >= PHASE_DAYS[-1]

        tlt = time.localtime()
        stlt = '{:d}{:02d}{:02d}{:02d}{:02d}{:02d}'.format(tlt.tm_year, tlt.tm_mon, tlt.tm_mday, 
                                                           tlt.tm_hour, tlt.tm_min, tlt.tm_sec)

        self.output_folder = os.path.join(os.getcwd(), 'Output', 
                                          args.input_file.split('/')[-1].split('_')[0], stlt)
        self.plots_folder = os.path.join(self.output_folder, 'Plots')
        self.vtables_folder = os.path.join(self.output_folder, 'VTables')

        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.plots_folder, exist_ok=True)
        os.makedirs(self.vtables_folder, exist_ok=True)
        
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir',self.vtables_folder)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
        
        self.wd = webdriver.Firefox(firefox_profile=profile)
        self.wd.get('http://www.cs.oberlin.edu/~rms/covid/main.html')
        
        self.mainframe = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'mainframe')))
        self.wd.switch_to.frame(self.mainframe)
        self.wd.find_element_by_id('loadSettings').send_keys(os.path.join(os.getcwd(), 'NMB_settings.dat'))
        print('Settings loaded')
        
        time.sleep(2) 
        datafile = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'datafile')))
        datafile.send_keys(os.path.join(os.getcwd(), args.input_file.replace('./', '')))
        time.sleep(2) 
        print('Data loaded')

        self.wd.execute_script('jumpto("opt")')

        self.error = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'error')))
        self.rguess = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'rguess')))
        self.g1 = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'g1')))
        self.accept = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'accept')))
        self.stop = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'stop')))
        wt = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'opt_weight_slider')))
        wt.value = '0'
        time.sleep(0.1)
        passed = False
        while not passed:
            try:
                self.wd.execute_script('optwtMonitor("0");')
                passed = True
            except:
                time.sleep(0.1)
        self.tmax = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'max')))
        self.tmin = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'min')))
        self.oframel = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'oframel')))
        self.cframe = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'cframe')))

    def _set_fixed(self):
        if self.phase in (2, 12): self.fixed['SocDist_steep'] = 3
        if self.phase == 3: self.fixed['SocRel_steep'] = 3
        if self.phase == 4: self.fixed['Surveil_steep'] = 2
        
        self.wd.switch_to.default_content()
        self.wd.switch_to.frame(self.mainframe)
        self.wd.switch_to.frame(self.cframe)

        for o in self.fixed:
            oo = (WebDriverWait(self.wd, 10)
                  .until(EC.presence_of_element_located((By.ID, '{}_field_Covid19DiscStoc_1'.format(o,)))))
            self.wd.execute_script('arguments[0].scrollIntoView();', oo)
            oo.clear()
            oo.send_keys(str(self.fixed[o]))
            
    def _do_rguess(self):

        self.wd.switch_to.default_content()
        self.wd.switch_to.frame(self.mainframe)
        self.wd.switch_to.frame(self.oframel)

        for o in BOUNDS:
            e = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, o)))
            self.wd.execute_script('arguments[0].scrollIntoView();', e)
            inc = (((self.phase in (1,12)) and (o in ['kappa','C_0','I_0','P_suc'])) or
                  ((self.phase in (2,12)) and o.startswith('SocDist_')) or
                  ((self.phase==3) and o.startswith('SocRel_')) or
                  ((self.phase==4) and o.startswith('Surveil_')))
            if inc:
                e.click()
                time.sleep(1)
                if not e.get_attribute('checked'): 
                    e.click()
                    time.sleep(1)
                self.wd.switch_to.default_content()
                self.wd.switch_to.frame(self.mainframe)
                self.tmin.clear()
                self.tmin.send_keys(str(BOUNDS[o][0]))
                self.tmax.clear()
                self.tmax.send_keys(str(BOUNDS[o][1]))
                self.rguess.click()
                time.sleep(0.1)
                self.accept.click()
                self.wd.switch_to.frame(self.oframel)
            elif e.get_attribute('checked'):
                e.click()
                
        print('Random guess done')

    def _phase_index(self):
        if self.phase in (1,12): return 0
        if self.phase == 2: return 1
        if self.phase == 3: return -2
        if self.phase == 4: return -1
        
    def _optimize(self):
        print('Optimization starting')
        self.wd.switch_to.default_content()
        self.wd.switch_to.frame(self.mainframe)
        frf = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'FitEnd_field')))
        self.wd.execute_script('fitRangeMonitor("end", {});'.format(PHASE_DAYS[self._phase_index()],))
        time.sleep(2) 
        
        o = WebDriverWait(self.wd, 10).until(EC.presence_of_element_located((By.ID, 'go')))
        self.wd.execute_script('arguments[0].scrollIntoView();', o)
        o.click()

        i = 0
        last = self.error.get_property('value')
        while i < 20:
            time.sleep(0.5)
            if last == self.error.get_property('value'):
                i += 1
            else:
                i = 0
                last = self.error.get_property('value')

        self.stop.click()
        print('Optimization finished')
        
    def _get_results(self):

        self.error = WebDriverWait(self.wd, 100).until(EC.presence_of_element_located((By.ID, 'error')))
        
        self.wd.switch_to.frame(self.cframe)       
        sh = (WebDriverWait(self.wd, 100)
              .until(EC.presence_of_element_located((By.ID, 'simhi_field_Covid19DiscStoc_1'))))
        self.wd.execute_script('arguments[0].scrollIntoView();', sh)

        time.sleep(1)

        while not sh.is_enabled(): 
            print('simhi disabled')
            time.sleep(1)

        self.wd.execute_script('simRangeMonitor("end", {});'.format(PHASE_DAYS[self._phase_index()],))

        time.sleep(1)

        runbt = self.wd.find_element_by_id('run_button_Covid19DiscStoc_1')
        self.wd.execute_script('arguments[0].scrollIntoView();', runbt)

        time.sleep(1)
        runbt.click()
        time.sleep(1)

        timeval = (WebDriverWait(self.wd, 10)
                   .until(EC.presence_of_element_located((By.ID, 'timeval_field_Covid19DiscStoc_1'))))
        self.wd.execute_script('arguments[0].scrollIntoView();', timeval)

        while int(timeval.get_property('value')) < PHASE_DAYS[self._phase_index()]: 
            print('timeval',timeval.get_property('value'))
            self.wd.execute_script('arguments[0].scrollIntoView();', timeval)
            runbt.click()
            time.sleep(1)

        tbl_inc = WebDriverWait(self.wd, 10).until(EC.presence_of_element_located((By.ID, 'Table_Covid19DiscStoc_1')))
        trs = tbl_inc.find_elements_by_xpath('./table//tbody//tr')[1:(PHASE_DAYS[self._phase_index()] + 2)]
        incs = ','.join([tr.find_elements_by_tag_name('td')[1].get_attribute('innerHTML') for tr in trs])        
        fill = ','.join([''] * (PHASE_DAYS[-1]-len(trs) + 2))
        datastr = ','.join([str(i) for i in self.data[0][:(PHASE_DAYS[self._phase_index()] + 1)]])

        p = {}
        if self.phase in (1, 12):
            for o in ['kappa', 'C_0', 'I_0', 'P_suc']:
                p[o] = (WebDriverWait(self.wd, 10)
                        .until(EC.presence_of_element_located((By.ID, '{}_field_Covid19DiscStoc_1'.format(o,))))
                        .get_property('value'))
        if self.phase in (2, 12):
            for o in ['SocDist_' + oo for oo in ['on', 'init', 'fnl', 'switch']]:
                p[o] = (WebDriverWait(self.wd, 10)
                        .until(EC.presence_of_element_located((By.ID, '{}_field_Covid19DiscStoc_1'.format(o,))))
                        .get_property('value'))
        if self.phase == 3:
            for o in ['SocRel_' + oo for oo in ['on', 'init', 'fnl', 'switch']]:
                p[o] = (WebDriverWait(self.wd, 10)
                        .until(EC.presence_of_element_located((By.ID, '{}_field_Covid19DiscStoc_1'.format(o,))))
                        .get_property('value'))
        if self.phase == 4:
            for o in ['Surveil_' + oo for oo in ['on', 'init', 'fnl', 'switch']]:
                p[o] = (WebDriverWait(self.wd, 10)
                        .until(EC.presence_of_element_located((By.ID, '{}_field_Covid19DiscStoc_1'.format(o,))))
                        .get_property('value'))
        self.phase_log['params'].append(p)
        
        savetbl = WebDriverWait(self.wd, 10).until(EC.presence_of_element_located((By.ID, 'savefile')))
        savetbl.send_keys(''.join([Keys.BACK_SPACE] * 50) + 'Phase_{}_Repeat_{}.csv'.format(self.phase, self.repeat))
        time.sleep(0.5)
        print('Table saved')
        
        fit_plot_span = (WebDriverWait(self.wd, 10)
                         .until(EC.presence_of_element_located((By.ID, 'Incidence_Covid19DiscStoc_1'))))
        self.wd.execute_script('arguments[0].scrollIntoView();', fit_plot_span)
        time.sleep(0.2)
        self.wd.save_screenshot(self.plots_folder + 'Phase_{}_Repeat_{}.png'.format(self.phase,self.repeat))
        print('Screenshot save')
        
        self.wd.switch_to.default_content()
        self.wd.switch_to.frame(self.mainframe)
        self.wd.execute_script('arguments[0].scrollIntoView();', self.error)
        error = self.error.get_property('value')
        print('Error = ' + error)
        self.phase_log['error'].append(float(error))
        self.output_file.write('{},{},{},{},{}{},{}{}{}'
                               .format(self.phase, 
                                       self.repeat,error, 
                                       ','.join([str(p[o]) 
                                                 if o in p else (self.fixed[o] if o in self.fixed else '') 
                                                 for o in BOUNDS]),
                                       incs,
                                       fill,
                                       datastr,
                                       fill,
                                       os.linesep))
        
    def _switch(self):
        self.wd.switch_to.default_content()
        self.wd.switch_to.frame(self.mainframe)
        self.wd.switch_to.frame(self.cframe)

        for name, state in [('SocDistancing', self.phase in (12, 2, 3, 4)),
                           ('SocRelaxation', self.phase in (3, 4)), 
                           ('Surveillance', self.phase == 4)]:

            swc = (WebDriverWait(self.wd, 10)
                   .until(EC.presence_of_element_located((By.ID, name + '_switch_Covid19DiscStoc_1'))))

            if swc.get_property('checked') != state: 
                self.wd.execute_script('arguments[0].setAttribute("style", "")', swc);
                self.wd.execute_script('arguments[0].setAttribute("class", "")', swc);
                self.wd.execute_script('arguments[0].scrollIntoView();', swc)
                swc.click()
                self.wd.execute_script('arguments[0].setAttribute("style", "visibility:hidden;")', swc);
                self.wd.execute_script('arguments[0].setAttribute("class", "switch")', swc);
                    
    def run(self):
        self.output_file = open(self.output_folder + 'results_log.csv', 'w')
        self.output_file.write('Run,Phase,Error,{}'.format(','.join([p for p in BOUNDS])))
        self.output_file.write(',{},{}'.format(','.join(['Sim day {}'.format(i,) for i in range(PHASE_DAYS[-1] + 1)]),
                                               ','.join(['Data day {}'.format(i,) for i in range(PHASE_DAYS[-1] + 1)])))
        self.output_file.write(os.linesep)
        self.phase = 1 if len(PHASE_DAYS) in (2, 4) else 12
        end_phase = 5 if len(PHASE_DAYS) in (3, 4) else 3
        self.fixed = {}
        while self.phase != end_phase:
            if PHASE_REPEATS[self._phase_index()] == 0:
                if self.phase in (1, 12): vs = ['kappa', 'C_0', 'I_0', 'P_suc']
                if self.phase in (2, 12): vs = ['SocDist_' + oo for oo in ['on', 'init', 'fnl', 'switch']]
                if self.phase == 3: vs = ['SocRel_' + oo for oo in ['on', 'init', 'fnl', 'switch']]
                if self.phase == 4: vs = ['Surveil_' + oo for oo in ['on', 'init', 'fnl', 'switch']]
                for o in vs:
                    self.fixed[o]=str(FIXED_VALUES[o])
                    print('Set {} = {}'.format(o, FIXED_VALUES[o]))                
            else:
                self.phase_log = {'error':[], 'params':[]}
                print('Phase {}'.format(self.phase,))
                self._switch()
                for rin in range (PHASE_REPEATS[self._phase_index()]):
                    self.repeat = rin + 1
                    print('Phase {} R {}'.format(self.phase, self.repeat))
                    self._do_rguess()
                    self._set_fixed()
                    self._optimize()
                    self._get_results()
                i = np.argmin(self.phase_log['error'])
                print('----------------------------')
                print('Min error: {}'.format(self.phase_log['error'][i],))
                for o in self.phase_log['params'][i]:
                    print('{} = {}'.format(o, self.phase_log['params'][i][o]))
                    self.fixed[o]=self.phase_log['params'][i][o]
                print('----------------------------')
            self.phase = 3 if self.phase == 12 else (self.phase + 1)
        self.output_file.close()
        self.phase -= 1
        self._do_rguess()
        self._set_fixed()
        
    def close(self):
        self.wd.close()
    

if __name__=='__main__':
    csa = CSA()
    csa.run()
    time.sleep(3)
    csa.close()