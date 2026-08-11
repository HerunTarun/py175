def delete_todo_by_id(todo_id, todo_list):
    todo_list['todos'] = [todo for todo in todo_list['todos']
                          if todo['id'] != todo_id]
    return None

def error_for_list_title(title, lists):
    if any(lst['title'] == title for lst in lists):
        return "The title must be unique."
    elif not 1 <= len(title) <= 100:
        return "The title must be between 1 and 100 characters"
    else:
        return None

def error_for_todo_title(title):
    if not 1 <= len(title) <= 100:
        return "The title must be between 1 and 100 characters"
    return None

def find_list_by_id(list_id, lists):
    return next((lst for lst in lists if lst['id'] == list_id), None)

def find_todo_by_id(todo_id, todos):
    return next((todo for todo in todos if todo['id'] == todo_id), None)

def is_list_completed(todo_list):
    return len(todo_list['todos']) > 0 and todos_remaining(todo_list) == 0

def mark_all_complete(todo_list):
    for todo in todo_list['todos']:
        todo['completed'] = True
    return None

def todos_remaining(lists):
    return sum(1 for todo in lists['todos']
               if not todo['completed'])