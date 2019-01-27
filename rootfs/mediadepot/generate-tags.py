import yaml
import io
import re
import requests
import os


username = os.environ['SISMICS_USERNAME']
password = os.environ['SISMICS_PASSWORD']
api_base = '{0}/api'.format(os.environ['SISMICS_BASE_URL'])

s = requests.Session()
r = s.post('{0}/user/login'.format(api_base), data={'username':username, 'password':password})
r.raise_for_status()
print r.json()


r = s.get('{0}/tag/list'.format(api_base))
r.raise_for_status()
print r.json()
existing_records = r.json()['tags']

def find_existing_record(tag_id, parent_tag_id):

    if parent_tag_id:
        return next(iter([r for r in existing_records if r['name'] == tag_id and r['parent'] == parent_tag_id]), None)
    else:
        return next(iter([r for r in existing_records if r['name'] == tag_id]), None)

def generate_tag_id(tag_label):
    return re.sub('[^A-Za-z0-9]+', '_', tag_label.lower())

def create_tag_rec(tag, parent_tag_id):
    tag_label = tag['label']
    tag_id = generate_tag_id(tag_label)

    tag_create_response = None


    existing_tag = find_existing_record(tag_id, parent_tag_id)
    if existing_tag:
        print "found existing tag: {0}".format(existing_tag['name'])
        tag_create_response = existing_tag
    else:
        if parent_tag_id:
            print "creating {0} with parent: {1}".format(tag_id, parent_tag_id)
            r = s.put('{0}/tag'.format(api_base), data={'name': tag_id, 'parent': parent_tag_id, 'color': tag['color']})
            r.raise_for_status()
            tag_create_response = r.json()
            print tag_create_response

        else:
            print "creating {0}".format(tag_id)
            r = s.put('{0}/tag'.format(api_base), data={'name': tag_id, 'color': tag['color']})
            r.raise_for_status()
            tag_create_response = r.json()
            print tag_create_response

    if 'tags' in tag:
        for tag_item in tag['tags']:
            tag_item['color'] = tag['color']
            create_tag_rec(tag_item, tag_create_response['id'])

def main():

    # https://www.thebalancecareers.com/how-to-organize-your-paperwork-3544878
    # https://www.reddit.com/r/datacurator/comments/a5ouiq/going_digital_with_documents/
    # https://www.reddit.com/r/datacurator/comments/8rd8fr/critique_my_planned_file_structure/


    # Read YAML file and generate tag
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "tag-structure.yaml"), 'r') as stream:
        tag_structure = yaml.load(stream)
        print tag_structure

        for tag_item in tag_structure['tags']:
            create_tag_rec(tag_item, None)

if __name__ == "__main__":
    main()