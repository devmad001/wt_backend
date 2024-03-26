import os, sys
import time
import unittest


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#sys.path.insert(0,LOCAL_PATH+"../../")

#sys.path.insert(0,LOCAL_PATH+"../../../" #logger
#from get_logger import setup_logging
#logging=setup_logging()


from case_state_objs import Case_Proxy
from case_state_objs import Cases_State_Manager
from case_pipeline import handle_FSM_case_processing_request
from case_pipeline import handle_FSM_case_admin_request


#0v1# JC Jan 11, 2023   Formal setup


"""
    *registered into global tests (event though within c_case_manager)
    TEST + DEV STATE MACHINE  (CASES PAGE)
    - Front-end specific
    (BE is more elaborate so need to keep separate for now)
    - optionally use mock cases to move around abstract queue (todo)

"""
 


class TestCASEProxy(unittest.TestCase):

    def setUp(self):
        pass
        #self.case_id = 123
        #self.case_proxy = CASE_Proxy(self.case_id)

    def test_set_state_key(self):
#        self.assertFalse(True)
        self.assertTrue(True)

        
class TestCASEStateManager(unittest.TestCase):

    def setUp(self):
        self.Manager = Cases_State_Manager()
        
    def test_list_cases(self):
        Case=None
        for Case in self.Manager.iter_cases():
            break
        self.assertNotEqual(Case,None)


class TestWorkflowCreateDelete(unittest.TestCase):

    def setUp(self):
        ## Shell instance
        self.case_id='test_case_123'
        self.username='test_user_123'
        self.Case=Case_Proxy(self.case_id)
        self.CManager=Cases_State_Manager()
        #Validate test user (ideally separate test for user space)
        self.CManager.create_user(self.username)

    def test_create_case_delete_case(self):
        simulated=False
    
        ## init_case (really just to check proxy object)
        action_type='init_case'  #Non details posted though
        did_update,meta=handle_FSM_case_processing_request(action_type,self.case_id,simulated=simulated,data=None)
        self.assertTrue('init_case' in meta['actions_log'])

        ## create_case via admin
        action_type='create_case'
        meta=handle_FSM_case_admin_request(action_type,self.case_id,username=self.username,simulated=simulated,data=None)
        
        ## Check case state
        case_state_dict=self.CManager.get_case_state_dict(self.case_id)
        self.assertTrue(len(case_state_dict)>0)
        
        ## Delete case
        action_type='delete_case'
        meta=handle_FSM_case_admin_request(action_type,self.case_id,simulated=simulated,data=None)
        self.assertTrue('deleted_case' in meta['actions_log'])

        ## Check case state
        case_state_dict=self.CManager.get_case_state_dict(self.case_id)
        self.assertFalse(len(case_state_dict)>0)


class TestCASEStateManager(unittest.TestCase):

    def setUp(self):
        self.Manager = Cases_State_Manager()
        
    def test_query_cases(self):
        #* will be slow unless load ALL case OBJECTs at once (or at least narrow active ones)
        start_time=time.time()

        ## Raw iterate db.all cases
        Case=None
        for Case in self.Manager.iter_cases(limit=1):
            break
        self.assertNotEqual(Case,None)
        
        ## Query cases
        case_db=None
        for case_db in self.Manager.query_cases(state_name='DONE'):
            break
        self.assertNotEqual(case_db,None)
        
        return


class TestCasesQueries(unittest.TestCase):

    def setUp(self):
        self.Manager = Cases_State_Manager()
        
    def test_query_cases(self):
        #* will be slow unless load ALL case OBJECTs at once (or at least narrow active ones)
        start_time=time.time()

        ## Raw iterate db.all cases
        Case=None
        for Case in self.Manager.iter_cases(limit=1):
            break
        self.assertNotEqual(Case,None)
        
        ## Query cases
        case_db=None
        for case_db in self.Manager.query_cases(state_name='DONE'):
            break
        self.assertNotEqual(case_db,None)
        
        return


class TestSimulateInitDoneDelete(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_init_done_delete(self):
        #1)  create case into init then have background into done then delete
        
        case_id='test_case_123'
        username='test_user_123'

        Case=Case_Proxy(case_id)
        
        ## Force to init then to done
        
        #> create
        action_type='create_case'
        meta=handle_FSM_case_admin_request(action_type,case_id,username=username)
        
        #> to init
        action_type='init_case'
        did_update,meta=handle_FSM_case_processing_request(action_type,case_id)
    
        #> to  done
        action_type='done_case'
        did_update,meta=handle_FSM_case_processing_request(action_type,case_id)
         
        Case=Case_Proxy(case_id)
        self.assertTrue(Case.is_state('DONE'))
        
        ## Delete case
        action_type='delete_case'
        meta=handle_FSM_case_admin_request(action_type,case_id)
        self.assertTrue('deleted_case' in meta['actions_log'])

        ## Check case state
        state,case_meta,case_state_dict=Case.get_state_info()
        self.assertFalse(len(case_state_dict)>0)

        return

    
##  Validate return variables for case status (at data level or later at api end)
#class TestCasesListStatusVariables(unittest.TestCase):
    


def dev_new_tests():
    print ("** dev_new_tests")

    ## Designing tests:
    #1)  create case into init then have background into done then delete
    
    case_id='test_case_123'
    username='test_user_123'
    Case=Case_Proxy(case_id)
    
    ## Force to init then to done
    
    #> create
    action_type='create_case'
    meta=handle_FSM_case_admin_request(action_type,case_id,username=username)
    
    #> to init
    action_type='init_case'
    did_update,meta=handle_FSM_case_processing_request(action_type,case_id)

    #> to init
    action_type='done_case'
    did_update,meta=handle_FSM_case_processing_request(action_type,case_id)
     
    Case=Case_Proxy(case_id)
    if not Case.is_state('DONE'):
        raise Exception('Case not in DONE state')

    else:
        print ("ok")
        
    #[ ] delete

    return



if __name__ == "__main__":
#    dev_new_tests()
    unittest.main()
    









