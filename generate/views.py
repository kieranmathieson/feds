import os
import errno
import zipfile
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseServerError, \
    HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from generate.feds_generator import FedsGenerator
from projects.models import ProjectDb
from feds.settings import DATA_SETS_LOCATION

def generate(request):
    # Get the project id from the post.
    project_id = request.POST.get('projectid', None)
    if project_id is None:
        return JsonResponse({'status': 'Error: project id missing'})
    # Check that the user has generate access.
    if not user_can_generate(request, project_id):
        return JsonResponse({'status': 'Error: access denied'})
    # Get the visible settings.
    visible_settings_stringed = request.POST.get('settingsstate', None)
    if visible_settings_stringed is None:
        return JsonResponse({'status': 'Error: settingsstate missing'})
    # Make a dictionary.
    visible_settings = json.loads(visible_settings_stringed)
    try:
        generator = FedsGenerator(project_id)
        # Create each of the tables with SQL.
        generator.create_customer_table()
        generator.create_product_table()
        generator.create_invoice_table()
        # Compute how many objects we need.
        # How many customers? One value.
        generator.get_num_customers_to_make()
        # How many products? One value.
        generator.get_num_products_to_make()
        # How many invoices for each customer? Dict.
        generator.get_num_invoices_per_customer()
        # First pass: correct data with given settings.
        generator.create_customers()
        generator.create_products()
        generator.get_num_invoices_per_customer()
        # Create a temp dir.
        module_dir = os.path.dirname(__file__)  # get current directory
        export_dir_path = os.path.join(module_dir,
                                       'generated/project' + str(project_id))
        # Make the dir if it does not exist.
        if not os.path.exists(export_dir_path):
            os.makedirs(export_dir_path)
        # Erase all files in it.
        erase_files_in_dir(export_dir_path)
        # Save customer data.
        generator.save_customer_data(export_dir_path, 'customers.csv')
        # Save product data.
        generator.save_product_data(export_dir_path, 'products.csv')
        # Make the project description document.
        generator.save_proj_spec_file(visible_settings,
                                      export_dir_path, 'project.html')
        # Zip all the things. Zip file is above the project dir, named
        # projectXXX.zip
        zip_file_path = get_path_to_project_archive(project_id)
        zip_dir(export_dir_path, zip_file_path)
        # Erase the files that were just zipped.
        erase_files_in_dir(export_dir_path)
        # Send the archive's path to the client.
        response = {
            'status': 'ok',
            'archiveurl': '/uploads/project' + str(project_id) + '.zip'
        }
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'status': 'Error: ' + e.__str__()})


@login_required
def user_can_generate(request, project_id):
    # Check whether the user has permission.
    # TODO: replace with permission check?
    # Is the owner of the project, or is staff?
    current_user = request.user
    project_db = get_object_or_404(ProjectDb, pk=project_id)
    project_owner = project_db.user
    if current_user == project_owner:
        return True
    if current_user.is_staff():
        return True
    return False


def erase_files_in_dir(dir_path):
    for the_file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            raise IOError('Could not erase "{fp}"'.format(fp=file_path))


def get_path_to_project_archive(project_id):
    app_dir = os.path.dirname(__file__)  # get current directory
    # Relative path from app dir to dir where data sets will be stores.
    relative_path = '/../' + DATA_SETS_LOCATION + '/'
    data_set_dir = os.path.realpath(app_dir + relative_path)
    # Make that dir if it isn't there.
    # See https://stackoverflow.com/questions/273192/how-can-i-create-a-directory-if-it-does-not-exist
    try:
        os.makedirs(data_set_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise IOError('get_path_to_project_archive: bad: ' + e.__str__())
    path = os.path.join(data_set_dir, 'project' + project_id + '.zip')
    return path


def zip_dir(export_dir_path, zip_file_path):
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(export_dir_path):
        for file in files:
            zipf.write(os.path.join(root, file), file)
    zipf.close()


def delete_archive(request):
    # Get the project id from the post.
    project_id = request.POST.get('projectid', None)
    if project_id is None:
        return JsonResponse({'status': 'Error: project id missing'})
    # Check that the user has generate access.
    if not user_can_generate(request, project_id):
        return JsonResponse({'status': 'Error: access denied'})
    try:
        zip_file_path = get_path_to_project_archive(project_id)
        os.unlink(zip_file_path)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'Error: ' + e.__str__()})
