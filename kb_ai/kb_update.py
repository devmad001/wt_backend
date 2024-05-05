import os
import sys
import codecs
import json
import re
import time

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from a_query.cypher_helper import cypher_add_fields_to_node
from a_query.cypher_helper_neo4j import cypher_add_fields_to_node_VERSIONS

from a_query.cypher_helper import cypher_create_node
from a_query.cypher_helper import cypher_create_update_node
from a_query.cypher_helper import cypher_create_relationship
from a_query.cypher_helper import cypher_add_create_relationship

from cypher_markups.markup_alg_cypher_EASY_CREDIT_DEBIT import is_transaction_credit #informal

from w_storage.gstorage.gneo4j import Neo
from schemas.SCHEMA_graph import GRAPH_SCHEMA


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep 17, 2023  Init


"""
    df to cypher for insert
    - keep generic so schema def can define insert query
    - _VERSIONS support to track field version changes (but requires neo4j)
           ^stored as a serialized json versions[key]='alg_version'
"""

"""
    TODO
    ====
    - Watch when sender or receiver id is missing
          logging.error("[error] sender or receiver id is required at: "+str(record))
"""


def dev_cypher_update(case_id='',node_label=None,kb_update_type='field_update',new_records=[],fields_to_update=[],schema={},markup_version='default', force_fields_to_update=True):
    """
        fields_to_update=[] if fields already exist!
    """
    meta={}

    ## Update always?
    #[ ] or check if exists
    #[ ] or check version is different

    if not fields_to_update and not force_fields_to_update:
        logging.info("[no fields to update in markup]")
        return

    elif not fields_to_update and force_fields_to_update:
        fields_to_update=schema['fields_to_update']
    else: pass


    # field_update:  Update the Node attributes  (rather then creating specifically)

    print ("SCHEMA: "+str(schema))

    ## Validate
    ## 1/  Select first target node to validate
    #[ ] tbd select node
    if not node_label: raise Exception("node_label is required")

    ## 2/  schema targets fields to update but may not be present
    if not set(fields_to_update).issubset(set(schema['fields_to_update'])):
        logging.warning("[cypher update]  fields_to_update not in schema: "+str(fields_to_update)+" vs: "+str(schema['fields_to_update']))

    if kb_update_type=='field_update':
        # Node field vs rel field?

        ## Mapping using lookup table of graph_schema?
        if node_label=='Transaction':  # [ ] hard code for now

            id_property_name=GRAPH_SCHEMA['node2id_name'][node_label]

            for record in new_records:
                ## Get sub dict given fields_to_upate
                properties={}
                for f in fields_to_update:
                    if record.get(f,''):
                        properties[f]=record.get(f,'') # May not be on all

                if properties:
                    #cypher=cypher_add_fields_to_node(node_label,properties, record[id_property_name])
                    print ("RECORD: "+str(record))


                    if 'add_field_and_version' in ['add_field_and_version']:
                        cypher=cypher_add_fields_to_node_VERSIONS(node_label,properties, record[id_property_name], version=markup_version, id_property_name=id_property_name)
                    else:
                        #Do without neo4j query
                        cypher=cypher_add_fields_to_node(node_label,properties, record[id_property_name], id_property_name=id_property_name)

#D#                    print ("[cypher dev]: "+str(cypher))

                    meta['count_updates']=meta.get('count_updates',0)+1
                    for rr in Neo.iter_stmt(cypher,verbose=True):
                        print ("[cypher] result: "+str(rr)) #Non on insert

        else:
            raise Exception("node_label not supported: "+str(node_label))
    elif kb_update_type=='node_create':
        # For Entity creation
        #- update Transaction field though with e_created=True or similar flag (for next processing or check versions on field)
        #? special type node_create or node_create_SR_entities


        ## See:  dev_add_nodes:
        #Nov 7 BufferError resize?? catch and retry ok
        try:
            handle_create_entity_receiver_sender(case_id=case_id,markedup_records=new_records)
        except Exception as e:
            logging.warning("Error on create receiver sender ?? buffer error? "+str(e))
            handle_create_entity_receiver_sender(case_id=case_id,markedup_records=new_records)

    else:
        raise Exception("kb_update_type not supported: "+str(kb_update_type))


    logging.info("[debug] possible freeze after create receiver sender?")
    return meta

def assign_main_account_entity_id(sender_type='',receiver_type='',sender_entity_id='',receiver_entity_id='',account_number=''):
    ## Assume id is main account id unless otherwise stated
    entity_id=''
    
    if sender_type=='main_account':
        entity_id=sender_entity_id
        if not entity_id:
            entity_id=account_number

    if receiver_type=='main_account':
        entity_id=receiver_entity_id
        if not entity_id:
            entity_id=account_number

    return entity_id


def clean_id(id_value):
    # Replace escaped apostrophes with single apostrophes
    id_value = re.sub(r"\\'", "'", id_value)
    # Replace single apostrophes with two single apostrophes for Cypher
    id_value = re.sub(r"'", "''", id_value)
    return id_value

def normalize_id_name(record):
    record['entity_id']=clean_id(record['entity_id'])
    record['name']=clean_id(record['name'])
    
    
    ## App specific but keep custom for now
    if 'custom_clean_ids' in ['custom_clean_ids']:
        #[M4] Hard code logical adjustments
        #- ie/ when not completely clear from data
        # Jpm[\d]+ is JP morgan id of transfer NOT account number
        record['entity_id']=re.sub('Jpm[\d]+','',record['entity_id']).strip()
        record['name']=re.sub('Jpm[\d]+','',record['name']).strip()
    print ("[NORM]: "+str(record))
    return record


def handle_create_entity_receiver_sender(case_id='',markedup_records=[]):
    # GIVEN: sender_entity_name # sender_entity_id # sender_entity_type, receiver_*

    ## RECORD:
    """
    {'transaction_date': '2021-12-02', 'filename_page_num': '3', 'receiver_id': 'case_3-000245202689 2128453290', 'transaction_amount': '', 'section': 'Deposits and other credits', 'transaction_method': 'other', 'statement_id': 'case_3-2021-12-01-3250 7713 0099-SGM-BOA-statement-december-2021.pdf-1', 'transaction_type': 'transfer', 'transaction_description': 'ACCOUNT TRANSFER TRSF FROM 000245202689 2128453290', 'filename': 'SGM-BOA-statement-december-2021.pdf', 'case_id': 'case_3', 'versions_metadata': '{"transaction_method": "llm_markup", "transaction_type": "llm_markup"}', 'payer_id': 'case_3-Bank Account', 'id': 'd9e776275a4a7de7d38ce71e4032ed43b292296b94bca370d58ba40190a71bbb', 'sender_entity_type': 'account', 'sender_entity_id': '000245202689', 'sender_entity_name': '', 'receiver_entity_type': 'main_account', 'receiver_entity_id': '', 'receiver_entity_name': ''}
    """

    cypher=''
    c=0
    rcount=0
    for record in markedup_records:
        c+=1

        print ("[kb_update RECORD]: "+str(record))

        record=final_catch_auto_resolve_sender(record) #Ie description "Desposit"

        print ("[kb_update RECORD++]: "+str(record))
        
        #########  PREPARE NODES

        ## SENDER NODE
        print ("[ ] check against SCHEMA..all field alus at least for now")
        sender={}
        sender['name']=record.get('sender_entity_name','')
        sender['entity_id']=record.get('sender_entity_id','')
        sender['type']=record.get('sender_entity_type','')
        sender['role']='SENDER'
        
        sender=normalize_id_name(sender)
    
        ## RECEIVER NODE
        receiver={}
        receiver['name']=record.get('receiver_entity_name','')
        receiver['entity_id']=record.get('receiver_entity_id','')
        receiver['type']=record.get('receiver_entity_type','')
        receiver['role']='RECEIVER'
        
        receiver=normalize_id_name(receiver)
    
        #### SENDER LOGICAL MAPPINGS
        
        ## MAIN ACCOUNT SENDER LOGIC
        ###== main_account sender!
        if sender['type']=='main_account':
            sender['role']='MAIN_ACCOUNT'
            sender['entity_id']=assign_main_account_entity_id(sender_type=sender['type'],receiver_type=receiver['type'],sender_entity_id=sender['entity_id'],receiver_entity_id=receiver['entity_id'],account_number=record.get('account_number',''))

        ###== cash sender! (ie/ cash deposity)
        if sender['type']=='cash':
            sender['role']='CASH'
            sender['entity_id']='cash' # physical cash account

        if not sender['entity_id']:
            sender['entity_id']=sender['name']
    

        ### RECEIVER LOGICAL MAPPINGS

        #[M1]
        ###== main_account receiver!
        if receiver['type']=='main_account':
            receiver['role']='MAIN_ACCOUNT'
            receiver['entity_id']=assign_main_account_entity_id(sender_type=sender['type'],receiver_type=receiver['type'],sender_entity_id=sender['entity_id'],receiver_entity_id=receiver['entity_id'],account_number=record.get('account_number',''))

        ###== cash receiver! (ie/ cash withdraw)
        if receiver['type']=='cash':
            receiver['role']='CASH'
            receiver['entity_id']='cash' # physical cash account

        
        #[M3] [ ] todo (can still query for main account role later)
        # [ ] map main_account to actual top account number (pass via ptr or transaction)
        #**see account_number or account id I suppose, or see what linked to transaction?
        if not record.get('account_id',''):
            #[ ] so will use the main_account as id for now
            logging.warning("[ ] MAIN account_id not included in transaction (likely old version)")
        else:
            logging.info("[ ] not linking transaction main_account to statement account (for now)")
            #main_account_node_id=record['account_id']  #case+account number

        #[M4]  Catch default value
        if not receiver['entity_id']:
            receiver['entity_id']=receiver['name']

        #[M5] add specific node ids
        sender['id']=case_id+"-"+sender['entity_id']
        receiver['id']=case_id+"-"+receiver['entity_id']

        ## VALIDATION
        #[V1]
        if not receiver['entity_id'] or not sender['entity_id']:
            print ("[kb_update.py V1] RECORD: "+str(record))
            print ("[kb_update.py V1] sender: "+str(sender))
            print ("[kb_update.py V1] receiver: "+str(receiver))
            print ("="*50)
            
            logging.error("[error] sender or receiver id is required at: "+str(record))
            continue
            raise Exception("sender or receiver id is required")

        #[V2]
        # entity type (other fields) should match approved schema


        ####  TRANSACTION CHECK
        transaction_node_id=record['id']  #Actual node id not transaction id
        transaction_amount=record['transaction_amount']

        ####  CREATE:  SENDER + RECEIVER ENTITIES
        #** (better to create prior to relationship inserts -- easier to match on)

        cypher=''
        cypher+=cypher_create_update_node('Entity',sender,node_var='sender'+str(c))
        cypher += ' WITH sender' + str(c) + ' '  # This line adds the WITH clause for separation ##Nov 7 patch
        cypher+=cypher_create_update_node('Entity',receiver,node_var='receiver'+str(c))
        
        ## Possible syntax error
        print ("[debug] create nodes: "+str(cypher))
        for rr in Neo.iter_stmt(cypher,verbose=True):
            print ("[cypher given]: "+str(cypher))
            print ("[cypher] result: "+str(rr)) #Non on insert
            raise Exception ("[expect no result on insert]")
        cypher=''



        ####  RELATION DEFINITIONS
        # DEBITED_FROM, CREDITED_TO, PROCESSED_BY (atm. has transaction.field this is extra)?
    
        edge_from={}
#        edge_from['label']='DEBITED_FROM'
#        edge_from['start_node']=sender['id']
#        edge_from['end_node']=transaction_node_id
        edge_from['amount']=transaction_amount
        edge_from['date']=record.get('transaction_date','')
    
        edge_to={}
#        edge_to['label']='CREDITED_TO'
#        edge_to['start_node']=transaction_node_id
#        edge_to['end_node']=receiver['id']
        edge_to['amount']=transaction_amount
        edge_to['date']=record.get('transaction_date','')


        ## SENDER -> TRANSACTION -> RECEIVER
        #** TRANSACTION NODE ALREADY CREATED: transaction_noe_id

        # Example usage:
        rel1_info = {
            'rel_props': edge_from,
            'from_node_label': 'Entity',
            'from_node_var': 'sender' + str(c),
            'from_node_id': sender['id'],   #ok?
            'to_node_id': transaction_node_id,
            'to_node_label': 'Transaction',
            'rel_var': 'r' + str(rcount),
            'rel_type': 'DEBIT_FROM'
        }
        
        rel2_info = {
            'rel_props': edge_to,
            'from_node_id': transaction_node_id,
            'from_node_label': 'Transaction',
            'to_node_var': 'receiver' + str(c),
            'to_node_label': 'Entity',
            'rel_var': 'r' + str(rcount + 1),
            'rel_type': 'CREDIT_TO',
            'to_node_id': receiver['id']  #?needed or use per var above?
        }
        
        print ("[debug rel1_info]: "+str(rel1_info))
        print ("[debug rel2_info]: "+str(rel2_info))

        update_field = "algList"
        update_value = "create_ERS" #Entity, Receiver, Sender

        cypher_rel = create_double_relationship(rel1_info, rel2_info, update_field, update_value)
        cypher+=cypher_rel

        print ("="*50)
        print(cypher)
        print ("^"*50)

        start_time=time.time()
        for rr in Neo.iter_stmt(cypher,verbose=True):
            print ("[cypher given]: "+str(cypher))
            print ("[cypher] result: "+str(rr)) #Non on insert
            raise Exception ("[expect no result on insert]")
        run_time=time.time()-start_time
        if run_time>0.08:
            print ("[insert time]: "+str(run_time))


#        print ("CYPHER: "+str(cypher))

        #### TODO:
        ## Hard code any other fields
        ## Hard code any other nodes  (ATM entity?)
    
        ## FIELD UPDATES (at end)
        #> set transaction.SR_created=True  #sender receiver

    
#    print ("[cypher dev INSERT Entity (Sender + Receiver)]: "+str(cypher))
#
#    for rr in Neo.iter_stmt(cypher,verbose=True):
#        print ("[cypher] result: "+str(rr)) #Non on insert

    logging.info("[done custom Entity create for receiver and sender] (?freeze after this?)")
    return

### CHALLENGE:
#- update both debit + credit at same time, single transaction match for efficiency
#- also, register that the algorithm was run (future will check if NEEDS to run)
#   ^ use variable alg string in a list.
#- one at a time is inefficient and could be one-sided if fails.

def create_double_relationship(rel1_info, rel2_info, update_field=None, update_value=None):
    cypher_query = ""
    
    # First Relationship
    from_node_var1 = rel1_info.get('from_node_var', None)
    rel_var1 = rel1_info.get('rel_var', 'r0')
    rel_props1 = rel1_info.get('rel_props', {})
    rel_props1_str = ", ".join([f"{key}: '{value}'" for key, value in rel_props1.items()])

    cypher_query += f"MATCH ({from_node_var1}:{rel1_info['from_node_label']}{{id: '{rel1_info['from_node_id']}'}})\n"
    cypher_query += f"MATCH (to_node1:{rel1_info['to_node_label']}{{id: '{rel1_info['to_node_id']}'}})\n"
    cypher_query += f"MERGE ({from_node_var1})-[{rel_var1}:{rel1_info['rel_type']} {{{rel_props1_str}}}]->(to_node1)\n"

    # Update Transaction node if necessary
    if update_field and update_value:
        cypher_query += f"SET to_node1.{update_field} = CASE\n"
        cypher_query += f"  WHEN NOT EXISTS(to_node1.{update_field}) THEN ['{update_value}']\n"
        cypher_query += f"  WHEN NOT '{update_value}' IN to_node1.{update_field} THEN to_node1.{update_field} + '{update_value}'\n"
        cypher_query += f"  ELSE to_node1.{update_field}\n"
        cypher_query += f"END\n"
    
    cypher_query += f"WITH to_node1\n"
    
    # Second Relationship
    to_node_var2 = rel2_info.get('to_node_var', None)
    rel_var2 = rel2_info.get('rel_var', 'r1')
    rel_props2 = rel2_info.get('rel_props', {})
    rel_props2_str = ", ".join([f"{key}: '{value}'" for key, value in rel_props2.items()])

    cypher_query += f"MATCH ({to_node_var2}:{rel2_info['to_node_label']}{{id: '{rel2_info['to_node_id']}'}})\n"
    cypher_query += f"MERGE (to_node1)-[{rel_var2}:{rel2_info['rel_type']} {{{rel_props2_str}}}]->({to_node_var2})\n"
    
    return cypher_query


    
def BUG_AT_CARRY_REL0_create_double_relationship(rel1_info, rel2_info, update_field=None, update_value=None):
    cypher_query = ""
    
    # First Relationship
    from_node_var1 = rel1_info.get('from_node_var', None)
    from_node_label1 = rel1_info.get('from_node_label', '')
    to_node_label1 = rel1_info.get('to_node_label', '')
    to_node_id1 = rel1_info.get('to_node_id', None)
    rel_var1 = rel1_info.get('rel_var', 'r1')
    rel_props1 = rel1_info.get('rel_props', {})
    rel_props1_str = ", ".join([f"{key}: '{value}'" for key, value in rel_props1.items()])
    
    cypher_query += f"MATCH ({from_node_var1}:{from_node_label1})\n" if from_node_label1 else f"MATCH ({from_node_var1})\n"
    cypher_query += f"MATCH (to_node1:{to_node_label1}{{id: '{to_node_id1}'}})\n" if to_node_label1 else f"MATCH (to_node1{{id: '{to_node_id1}'}})\n"
    cypher_query += f"MERGE ({from_node_var1})-[{rel_var1}:{rel1_info['rel_type']} {{{rel_props1_str}}}]->(to_node1)\n"
    
    # Update Transaction node if necessary
    if update_field and update_value:
        cypher_query += f"SET to_node1.{update_field} = CASE\n"
        cypher_query += f"  WHEN NOT EXISTS(to_node1.{update_field}) THEN ['{update_value}']\n"
        cypher_query += f"  WHEN NOT '{update_value}' IN to_node1.{update_field} THEN to_node1.{update_field} + '{update_value}'\n"
        cypher_query += f"  ELSE to_node1.{update_field}\n"
        cypher_query += f"END\n"
    
    # Carry forward the created relationship and the 'to_node1'
    cypher_query += "WITH r0, to_node1\n"
    
    # Second Relationship
    from_node_id2 = rel2_info.get('from_node_id', None)
    from_node_label2 = rel2_info.get('from_node_label', '')
    to_node_var2 = rel2_info.get('to_node_var', None)
    to_node_label2 = rel2_info.get('to_node_label', '')
    rel_var2 = rel2_info.get('rel_var', 'r2')
    rel_props2 = rel2_info.get('rel_props', {})
    rel_props2_str = ", ".join([f"{key}: '{value}'" for key, value in rel_props2.items()])
    
    cypher_query += f"MATCH ({to_node_var2}:{to_node_label2})\n" if to_node_label2 else f"MATCH ({to_node_var2})\n"
    cypher_query += f"MERGE (to_node1)-[{rel_var2}:{rel2_info['rel_type']} {{{rel_props2_str}}}]->({to_node_var2})\n"
    
    return cypher_query



def local_has_main(record):
    ## Check for sender or receiver
    main_account_credit=False
    main_account_debit=False
    if 'main_account' in record.get('sender_entity_type',''):
        main_account_debit=True
    elif 'main_account' in record.get('sender_entity_id',''):
        main_account_debit=True
    elif 'main_account' in record.get('sender_entity_name',''):
        main_account_debit=True

    if 'main_account' in record.get('receiver_entity_type',''):
        main_account_credit=True
    elif 'main_account' in record.get('receiver_entity_id',''):
        main_account_credit=True
    elif 'main_account' in record.get('receiver_entity_name',''):
        main_account_credit=True

    return main_account_credit,main_account_debit


def final_catch_auto_resolve_sender(record):
    ###[ ] optionally move upstream but keep as-needed basis for now

    ## Recall, we've already done: transaction_type, transaction_method, sender + receiver via LLM
    #- this will basically just fill in "UNKNOWN" or possibly cash??
    
    ## LOGIC FOR CASE:  'chase_4_a_33' whereby 15150 transaction JUST says 'Deposit'
    
    main_account_credit,main_account_debit=local_has_main(record)
   
    #####################################
    #  PASS #1:  Unknown sender resolve
    #####################################
    ## Candidate?
    candidate=True
    if record.get('sender_entity_id','')=='' and record.get('sender_entity_type','')=='OTHER' and record.get('sender_entity_name','')=='':
        ## Other
        candidate=True
    elif record.get('sender_entity_id','') or record.get('sender_entity_type','') or record.get('sender_entity_name',''):
        candidate=False
    else:
        candidate=True

    ## Use standard transaction classifier (of course, won't use nodes)
    is_credit,tconfig,reasons=is_transaction_credit(record)

    ## NO SENDER BUT CREDIT
    if candidate:
        
        ## Ideally would have already been set by LLM
        if is_credit:
            ## Heuristic resolve sender BASIC!
            #** especially since it should not happen at db insert point -- Ideally, move upstream
            #- but, since directly relates to creating a NODE then include here for now
            
            logging.dev("[No sender so assume unknown deposit]: "+str(record))
    
            ## DEPOSIT FROM UNKNOWN PATH
            #- can also check if receiver is main_account, or types etc.
            ## Deposit from unknown
    
            record['sender_entity_type'] = record.get('sender_entity_type') or 'unknown'
            record['sender_entity_id'] = record.get('sender_entity_id') or 'unknown'
            record['sender_entity_name'] = record.get('sender_entity_name') or 'unknown'
            
            ## Fine tune?  Look for ATM or Cash mention or assume cash??
            #[ ] as required extend
            if 'ATM' in str(record) or re.search(r'\bcash',record.get('transaction_description',''),re.IGNORECASE):
                record['sender_entity_type']='cash'
                record['sender_entity_id']='cash'
                record['sender_entity_name']='cash'
    
        print ("RECORD IS CREDIT: "+str(record.get('is_credit',''))+" or: "+str(is_credit)) #**happens after this
    else:
        pass
    
    # refresh
    main_account_credit,main_account_debit=local_has_main(record)

    #####################################
    #  PASS #2:  Assume/find main_account  (should have this logic upstream)
    #####################################
    #[ ] 
    if not is_credit and not main_account_credit and not main_account_debit:
        ## Debit but main account not involved
        #-
        record['sender_entity_type'] = record.get('sender_entity_type') or 'main_account'
        record['sender_entity_id'] = record.get('sender_entity_id') or 'main_account'
        record['sender_entity_name'] = record.get('sender_entity_name') or 'main_account'

    if is_credit and not main_account_credit and not main_account_debit:
        ## Debit but main account not involved
        #-
        record['receiver_entity_type'] = record.get('receiver_entity_type') or 'main_account'
        record['receiver_entity_id'] = record.get('receiver_entity_id') or 'main_account'
        record['receiver_entity_name'] = record.get('receiver_entity_name') or 'main_account'

    # refresh
    main_account_credit,main_account_debit=local_has_main(record)
    #####################################
    #  PASS #3:  Set as unknown if one side is main_account  (just not on both sides)
    #####################################
    if main_account_credit and not record.get('sender_entity_name'):
        record['sender_entity_type'] = record.get('sender_entity_type') or 'unknown'
        record['sender_entity_id'] = record.get('sender_entity_id') or 'unknown'
        record['sender_entity_name'] = record.get('sender_entity_name') or 'unknown'

    elif main_account_debit and not record.get('receiver_entity_name'):
        record['receiver_entity_type'] = record.get('receiver_entity_type') or 'unknown'
        record['receiver_entity_id'] = record.get('receiver_entity_id') or 'unknown'
        record['receiver_entity_name'] = record.get('receiver_entity_name') or 'unknown'
    
    
    #####################################
    #  PASS #4:  If not main accounts and debit then set to main
    #####################################
    ## ** exception bad where usually SHOULD be main debit but is not:
    #{ ]  case_4_a page 56  Employment Devel description}
    if record.get('sender_entity_name',''):
        if not is_credit and not main_account_debit:
            record['sender_entity_type'] = record.get('sender_entity_type') or 'unknown'
            record['sender_entity_id'] = record.get('sender_entity_id') or 'unknown'
            record['sender_entity_name'] = record.get('sender_entity_name') or 'unknown'
            
    ## PASS #5 if no receiver but sender and thinks is_credit=False.
    #- don't enforce main account but note warning
    if not is_credit and record.get('sender_entity_name','') and not record.get('receiver_entity_name',''):
        if not is_credit and not main_account_debit:
            logging.dev("[warning] debit but not from main account: "+str(record))

        record['receiver_entity_type'] = record.get('receiver_entity_type') or 'unknown'
        record['receiver_entity_id'] = record.get('receiver_entity_id') or 'unknown'
        record['receiver_entity_name'] = record.get('receiver_entity_name') or 'unknown'


    # refresh
    main_account_credit,main_account_debit=local_has_main(record)
    #####################################
    #  PASS #X:  Raise error otherwise
    #####################################
    if not record.get('sender_entity_name','') and not record.get('receiver_entity_name',''):
        print ("[error] no sender or receiver: "+str(record))
        is_credit,tconfig,reasons=is_transaction_credit(record)
        print ("[debug] is credit: "+str(is_credit))
        raise Exception("no sender or receiver")
    
    if True: 
        print ("[kb_update debug] is credit: "+str(is_credit))
        print ("[kb_update debug] main credit: "+str(main_account_credit))
        print ("[kb_update debug] main debit: "+str(main_account_debit))

    return record


def call_auto_resolve_sender():
    sample_no_sender={'is_credit': True, 'filename_page_num': 1, 'transaction_date': '2015-05-08', 'account_number': '000000661956891', 'transaction_amount': 15150.0, 'section': 'Deposits and Additions', 'label': 'Transaction', 'transaction_method': 'other', 'statement_id': 'chase_4_a_33-2015-05-01-000000661956891-Chase Statements 4 12.pdf', 'transaction_type': 'deposit', 'transaction_description': 'Deposit', 'account_id': 'chase_4_a_33-000000661956891', 'filename': 'Chase Statements 4 12.pdf', 'case_id': 'chase_4_a_33', 'versions_metadata': '{"transaction_method": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': 'unknown', 'id': 'a9aa623fd77d3315651a10ae4644dc7c197a2fc3c379d1f7efa28f250076951c', 'sender_entity_type': '', 'sender_entity_id': '', 'sender_entity_name': '', 'receiver_entity_type': 'main_account', 'receiver_entity_id': 'main_account', 'receiver_entity_name': 'main_account'}

#    record=final_catch_auto_resolve_sender(sample_no_sender)
    
    sample_other_sender={'filename_page_num': 1, 'transaction_date': '2014-11-14', 'account_number': '000000661956891', 'transaction_amount': 10000.0, 'section': 'Deposits and Additions', 'label': 'Transaction', 'transaction_method': 'other', 'statement_id': 'chase_4_a-2014-11-14-000000661956891-Chase Statements 4.pdf', 'transaction_type': 'deposit', 'transaction_description': 'Deposit', 'account_id': 'chase_4_a-000000661956891', 'filename': 'Chase Statements 4.pdf', 'case_id': 'chase_4_a', 'versions_metadata': '{"transaction_method": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': 'unknown', 'id': 'b3e39705e77087f0eb16ef2b5cf99e971914f6493e501b8f9a5ef785b155b072', 'sender_entity_type': 'OTHER', 'sender_entity_id': '', 'sender_entity_name': '', 'receiver_entity_type': 'MAIN_ACCOUNT', 'receiver_entity_id': 'main_account', 'receiver_entity_name': 'main_account'}
#    record=final_catch_auto_resolve_sender(sample_other_sender)

    record= {'filename_page_num': 10, 'transaction_date': '2015-01-05', 'account_number': '000000661956891', 'transaction_amount': 680.0, 'section': 'CHECKS PAID', 'label': 'Transaction', 'transaction_method': 'check', 'statement_id': 'chase_4_a-2015-01-01-000000661956891-Chase Statements 4.pdf', 'transaction_type': 'payment', 'transaction_description': 'CHECK NO. 10021 A', 'account_id': 'chase_4_a-000000661956891', 'filename': 'Chase Statements 4.pdf', 'case_id': 'chase_4_a', 'versions_metadata': '{"transaction_method": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': '10021 A', 'id': '89e7e7e912d9b50a849c4582c2387e6470a4909c89a1e0575d87f5eb5d93cdde', 'sender_entity_type': 'individual', 'sender_entity_id': '', 'sender_entity_name': '', 'receiver_entity_type': 'check', 'receiver_entity_id': '10021', 'receiver_entity_name': ''}
    

    record= {'filename_page_num': 10, 'transaction_date': '2015-01-20', 'account_number': '000000661956891', 'transaction_amount': 1823.16, 'section': 'CHECKS PAID', 'label': 'Transaction', 'transaction_method': 'check', 'statement_id': 'chase_4_a-2015-01-01-000000661956891-Chase Statements 4.pdf', 'transaction_type': 'payment', 'transaction_description': 'CHECK NO. 10065 A', 'account_id': 'chase_4_a-000000661956891', 'filename': 'Chase Statements 4.pdf', 'case_id': 'chase_4_a', 'versions_metadata': '{"transaction_method": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': '10065', 'id': 'e44e975339fe316fdbea129b9f9c81701defbf1c6538bd22f45451b008e17233', 'sender_entity_type': 'individual', 'sender_entity_id': 'main_account', 'sender_entity_name': 'main_account', 'receiver_entity_type': 'vendor', 'receiver_entity_id': '', 'receiver_entity_name': ''}

    record= {'filename_page_num': 10, 'transaction_date': '2015-01-20', 'account_number': '000000661956891', 'transaction_amount': 1823.16, 'section': 'CHECKS PAID', 'label': 'Transaction', 'transaction_method': 'check', 'statement_id': 'chase_4_a-2015-01-01-000000661956891-Chase Statements 4.pdf', 'transaction_type': 'payment', 'transaction_description': 'CHECK NO. 10065 A', 'account_id': 'chase_4_a-000000661956891', 'filename': 'Chase Statements 4.pdf', 'case_id': 'chase_4_a', 'versions_metadata': '{"transaction_method": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': '10065', 'id': 'e44e975339fe316fdbea129b9f9c81701defbf1c6538bd22f45451b008e17233', 'sender_entity_type': 'individual', 'sender_entity_id': '', 'sender_entity_name': '', 'receiver_entity_type': 'vendor', 'receiver_entity_id': '', 'receiver_entity_name': ''}
    
    #[x] fixed upstream    record={'filename_page_num': 6, 'transaction_date': '2014-12-22', 'account_number': '000000661956891', 'transaction_amount': 1038.24, 'section': 'Electronic Withdrawals', 'label': 'Transaction', 'transaction_method': 'online_payment', 'statement_id': 'chase_4_a-2014-12-31-000000661956891-Chase Statements 4.pdf', 'transaction_type': 'payment', 'transaction_description': 'Irs Usataxpymt 220475655216495 CCD ID: 3387702000', 'account_id': 'chase_4_a-000000661956891', 'filename': 'Chase Statements 4.pdf', 'case_id': 'chase_4_a', 'versions_metadata': '{"transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-", "transaction_method": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': '3387702000', 'id': '480c6baa10d32f15c98a42eb0012b87b48cf7827c38348d39451e4109601f355', 'sender_entity_type': 'organization', 'sender_entity_name': 'Irs Usataxpymt', 'sender_entity_id': '3387702000', 'receiver_entity_type': 'credit_card', 'receiver_entity_name': '', 'receiver_entity_id': ''}

    record={'filename_page_num': 56, 'transaction_date': '2015-10-02', 'account_number': '000000661956891', 'transaction_amount': 32.71, 'section': 'Electronic Withdrawals', 'label': 'Transaction', 'transaction_method': 'other', 'statement_id': 'chase_4_a-2015-10-01-000000661956891-Chase Statements 4.pdf', 'transaction_type': 'withdrawal', 'transaction_description': 'Employment Devel Edd Eftpmt 59347072 CCD ID: 2282533055', 'account_id': 'chase_4_a-000000661956891', 'filename': 'Chase Statements 4.pdf', 'is_wire_transfer': True, 'case_id': 'chase_4_a', 'versions_metadata': '{"transaction_method": "llm_markup-transaction_type_method_goals-", "transaction_method_id": "llm_markup-transaction_type_method_goals-", "transaction_type": "llm_markup-transaction_type_method_goals-", "is_wire_transfer": "llm_markup-transaction_type_method_goals-"}', 'transaction_method_id': '59347072', 'id': '113f0e31cb89e1b6c0dd669cc763bed07c9bf502ea140d1632df33755310d0f7', 'sender_entity_type': 'organization', 'sender_entity_id': '2382533055', 'sender_entity_name': 'Employment Devel Edd Eftpmt', 'receiver_entity_type': 'other', 'receiver_entity_id': '', 'receiver_entity_name': ''}
    
    record=final_catch_auto_resolve_sender(record)
    print ("GOT: "+str(record))
    return

def dev_test_query():
    #[ ] fix downstream run_stmt to do '' -> \' required swap even though '' is valid cypher
    stmt="""MERGE (sender1:Entity {id: 'chase_5_a-Card 1287'}) ON CREATE SET sender1 += {name: 'main_account', entity_id: 'Card 1287', type: 'debit_card', role: 'SENDER', id: 'chase_5_a-Card 1287', label: 'Entity'} ON MATCH SET sender1 += {name: 'main_account', entity_id: 'Card 1287', type: 'debit_card', role: 'SENDER', id: 'chase_5_a-Card 1287', label: 'Entity'} WITH sender1 MERGE (receiver1:Entity {id: 'chase_5_a-Wal Sam''s Club 141'}) ON CREATE SET receiver1 += {name: 'Wal Sam''s Club 141', entity_id: 'Wal Sam''s Club 141', type: 'organization', role: 'RECEIVER', id: 'chase_5_a-Wal Sam''s Club 141', label: 'Entity'} ON MATCH SET receiver1 += {name: 'Wal Sam''s Club 141', entity_id: 'Wal Sam''s Club 141', type: 'organization', role: 'RECEIVER', id: 'chase_5_a-Wal Sam''s Club 141', label: 'Entity'}"""
    print ("TEST: "+str(stmt))
#    stmt=re.sub(r"''",r"'",stmt)
    rr=Neo.run_stmt(stmt)

    return
if __name__=='__main__':
    branches=['dev1']
    branches=['dev_sample_create_nodes']
    branches=['call_auto_resolve_sender']

    branches=['dev_test_query']

    for b in branches:
        globals()[b]()



"""
"""
