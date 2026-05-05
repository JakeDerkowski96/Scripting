#!/bin/bash

# Function to list all users and their group memberships
list_users_and_groups() {
    # Get all users from /etc/passwd
    local users=$(cut -d: -f1 /etc/passwd)

    # Iterate through each user and get their groups
    for user in $users; do
        echo "User: $user"
        groups $user 2>/dev/null || echo "Error retrieving groups for user: $user"
        echo ""
    done
}

# Execute the function
list_users_and_groups
