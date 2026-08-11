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

def is_todo_completed(todo):
    return todo['completed']

def mark_all_complete(todo_list):
    for todo in todo_list['todos']:
        todo['completed'] = True
    return None

def sort_items(items, select_complete):
    sorted_items = sorted(items, key=lambda item: item['title'].lower())

    incomplete_items = [item for item in sorted_items
                        if not select_complete(item)]
    complete_items = [item for item in sorted_items
                        if select_complete(item)]

    return incomplete_items + complete_items

def todos_remaining(lists):
    return sum(1 for todo in lists['todos']
               if not todo['completed'])