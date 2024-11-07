#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

###############################################
#
# Meal Management
#
###############################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating meal: $meal ($cuisine, \$$price, $difficulty)..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\",\"cuisine\":\"$cuisine\",\"price\":$price,\"difficulty\":\"$difficulty\"}")
  
  # Extract and display the meal ID if creation was successful
  if echo "$response" | grep -q '"status": "success"'; then
    meal_id=$(echo "$response" | jq -r '.meal_id // empty')
    echo "Meal created successfully with ID: $meal_id"
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Note: Failed to create meal. Continuing with tests..."
  fi
}

delete_meal() {
  meal_id=$1
  echo "Deleting meal ID: $meal_id..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1
  echo "Getting meal by ID: $meal_id..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1
  echo "Getting meal by name: $meal_name..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Note: Failed to get meal by name. Continuing with tests..."
  fi
}

test_battle() {
    echo "Clearing previous combatants..."
    curl -s -X POST "$BASE_URL/clear-combatants"

    echo "Preparing first combatant..."
    curl -s -X POST "$BASE_URL/prep-combatant" \
        -H "Content-Type: application/json" \
        -d "{\"meal\":\"$1\"}"

    echo "Preparing second combatant..."
    curl -s -X POST "$BASE_URL/prep-combatant" \
        -H "Content-Type: application/json" \
        -d "{\"meal\":\"$2\"}"

    echo "Getting current combatants..."
    curl -s "$BASE_URL/get-combatants"

    echo "Initiating battle..."
    response=$(curl -s "$BASE_URL/battle")
    echo "Battle result: $response"
}

check_leaderboard() {
    echo "Checking leaderboard..."
    response=$(curl -s "$BASE_URL/leaderboard")
    echo "Leaderboard: $response"
}

list_all_meals() {
  echo "Listing all meals..."
  response=$(curl -s -X GET "$BASE_URL/list-meals")
  
  if [ "$ECHO_JSON" = true ]; then
    echo "$response" | jq .
  else
    # Pretty print just the essential information
    echo "$response" | jq -r '.meals[] | "ID: \(.id) - \(.meal) (\(.cuisine))"'
  fi
}

clear_catalog() {
  echo "Clearing meal catalog..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Catalog cleared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to clear catalog."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  fi
}

###############################################
#
# Run the smoke tests
#
###############################################

# Health checks
check_health
check_db

clear_catalog

# Create various meals
create_meal "Spaghetti Carbonate sauce" "Italian" 15.99 "MED"
get_meal_by_id 1
create_meal "Sushi This" "Japanese" 22.99 "HIGH"
create_meal "Caesar salad" "American" 12.99 "LOW"
create_meal "Pad" "Thai" 16.99 "MED"
create_meal "Chicken Burger" "American" 13.99 "LOW"

# List all meals to see their IDs

get_meal_by_name "Spaghetti%20Carbo"

# Get meals by ID
get_meal_by_id 1
get_meal_by_id 2
get_meal_by_id 3

# Test battle functionality
test_battle "Spaghetti Carbonara" "Kung Pao Chicken"

# Check leaderboard
check_leaderboard

# Get leaderboard sorted different ways

# Delete a meal
delete_meal 1

# Create a new meal after deletion
create_meal "Fish and Chips" "British" 17.99 "MED"

# Final leaderboard check
get_leaderboard "wins"

# List all meals
list_all_meals

# Clear the catalog
clear_catalog

echo "All smoke tests completed successfully!"