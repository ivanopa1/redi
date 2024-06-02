<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lake Temperatures</title>
    <!-- Include Bootstrap CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-5">
    <h2 class="mb-4">Lake Temperatures</h2>

    <?php
    $conn = mysqli_connect("pharmcon.mysql.tools", "pharmcon_lake", "fakepass4", "pharmcon_lake");

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Define the number of results per page
    $results_per_page = 10;

    // Find out the number of results stored in the database
    $result = $conn->query("SELECT COUNT(DISTINCT lake, link) AS total FROM bavarianlakes WHERE timestamp = (SELECT MAX(timestamp) from bavarianlakes)");
    $row = $result->fetch_assoc();
    $total_results = $row['total'];

    // Determine number of total pages available
    $total_pages = ceil($total_results / $results_per_page);

    // Determine which page number visitor is currently on
    $current_page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
    if ($current_page < 1) {
        $current_page = 1;
    } elseif ($current_page > $total_pages) {
        $current_page = $total_pages;
    }

    // Determine the SQL LIMIT starting number for the results on the displaying page
    $starting_limit = ($current_page - 1) * $results_per_page;

    // Retrieve selected results from database and display them on page
    $sql = "SELECT * FROM (
                SELECT UPPER(lake) as LAKE, link as LINK, temp as CURRENT_TEMP, timestamp as DATETIME 
				FROM bavarianlakes WHERE timestamp = (SELECT MAX(timestamp) from bavarianlakes)
                ORDER BY timestamp DESC
            ) abc
            ORDER BY abc.CURRENT_TEMP DESC
            LIMIT $starting_limit, $results_per_page";

    $result = $conn->query($sql);
    ?>

    <table class="table table-striped table-bordered">
        <thead class="thead-dark">
            <tr>
                <th>LAKE</th>
                <th>CURRENT TEMP</th>
				<th>DATETIME</th>
            </tr>
        </thead>
        <tbody>
        <?php
        if ($result->num_rows > 0) {
            while ($row = $result->fetch_assoc()) {
                echo '<tr>';
                echo '<td><a href="' . $row["LINK"] . '">' . $row["LAKE"] . '</a></td>';
                echo '<td>' . $row["CURRENT_TEMP"] . '</td>';
				echo '<td>' . $row["DATETIME"] . '</td>';
                echo '</tr>';
            }
        } else {
            echo '<tr><td colspan="2">No Results</td></tr>';
        }
        $conn->close();
        ?>
        </tbody>
    </table>

    <!-- Pagination -->
    <nav>
        <ul class="pagination justify-content-center">
            <?php
            for ($page = 1; $page <= $total_pages; $page++) {
                $active = ($page == $current_page) ? 'active' : '';
                echo '<li class="page-item ' . $active . '"><a class="page-link" href="index.php?page=' . $page . '">' . $page . '</a></li>';
            }
            ?>
        </ul>
    </nav>
</div>
<!-- Include Bootstrap JS and dependencies -->
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
