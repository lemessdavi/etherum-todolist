// SPDX-License-Identifier: MIT

pragma solidity 0.8.15;

pragma experimental ABIEncoderV2;

contract TaskContract {
    event AddTask(address recipient, uint taskId);
    event DeleteTask(uint taskId, bool isDeleted);
    event CheckTask(uint taskId, bool isChecked);

    struct Task {
        uint id;
        string taskText;
        bool isChecked;
        bool isDeleted;
    }

    Task[] public tasks;
    mapping(uint256 => address) taskToOwner;

    function addTask(string memory taskText, bool isChecked, bool isDeleted) external {
        uint taskId = tasks.length;
        tasks.push(Task(taskId, taskText, isChecked, isDeleted));
        taskToOwner[taskId] = msg.sender;
        emit AddTask(msg.sender, taskId);
    }


    function getMyTasks() external view returns (Task[] memory){
        Task[] memory temporary = new Task[](tasks.length);
        uint counter = 0;
        for(uint i=0; i<tasks.length; i++){
            temporary[counter] = tasks[i];
                counter++;
        }
        Task[] memory result = new Task[](counter);
        for(uint i = 0; i < counter; i++) {
            result[i] = temporary[i];
        }

        return result;
    }

    function deleteTask(uint taskId, bool isDeleted) external {
        if(taskToOwner[taskId] == msg.sender){
            tasks[taskId].isDeleted = isDeleted;
            emit DeleteTask(taskId, isDeleted);
        }
    }

    function checkTask(uint taskId, bool isChecked) external {
        if(taskToOwner[taskId] == msg.sender){
            tasks[taskId].isChecked = isChecked;
            emit CheckTask(taskId, isChecked);
        }
    }

    

}