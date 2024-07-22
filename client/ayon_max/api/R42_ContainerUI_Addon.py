R42_CONTAINER_UI_POPUP = """rollout AyonContainerEdit "AYON Container Edit" width:780 height:570
(
	/*--------------
	   VARIABLES
	--------------*/
	local current_handles = #()
	local current_self
	local current_modifier

	/*--------------
	   PARAMS
	--------------*/
	multiListBox  lb_camera "Scene Camera" items:#() width:150 height:15 pos:[10,10]
	multiListBox  lb_object "Scene Objects" items:#() width:150 height:15 pos:[10,260]
	multiListBox  lb_tycache "Scene Tycaches" items:#() width:150 height:15 pos:[410,10]
	multiListBox  lb_lights "Scene Lights" items:#() width:150 height:15 pos:[410,260]

	multiListBox  lb_con_camera "Container Camera" items:#() width:150 height:15 pos:[210,10]
	multiListBox  lb_con_object "Container Objects" items:#() width:150 height:15 pos:[210,260]
	multiListBox  lb_con_tycache "Container Tycache" items:#() width:150 height:15 pos:[610,10]
	multiListBox  lb_con_lights "Container Lights" items:#() width:150 height:15 pos:[610,260]

	button b_camera_in ">>" pos:[170,100]
	button b_camera_out "<<" pos:[170,130]
	button b_object_in ">>" pos:[170,340]
	button b_object_out "<<" pos:[170,370]
	button b_tycache_in ">>" pos:[570,100]
	button b_tycache_out "<<" pos:[570,130]
	button b_light_in ">>" pos:[570,340]
	button b_light_out "<<" pos:[570,370]

	button b_accept "Accept" width:100 height:30 pos:[550,510]
	button b_cancel "Cancel" width:100 height:30 pos:[660,510]

	/*--------------
	   Functions
	--------------*/
	fn sortObjects obj &obj_array &camera_array &light_array &tycache_array =
	(
		if (superClassOf obj) == camera then
		(
			append camera_array obj.name
		)
		else if (superClassOf obj) == GeometryClass and (classOf obj) == Targetobject then
		(
			append camera_array obj.name
		)
		else if (superClassOf obj) == light then
		(
			append light_array obj.name
		)
		else if(classOf obj) == tyFlow then
		(
			append tycache_array obj.name
		)
		else
		(
			append obj_array obj.name
		)
	)

	fn sortLightTargets &light_array &camera_array =
	(
		for l in light_array do
		(
			target_name = l + ".Target"
			found = findItem camera_array target_name
			if found > 0 then
			(
				append light_array target_name
				deleteItem camera_array found
			)
		)
		print light_array

	)

	fn moveObjects &source_multilist &dest_multilist =
	(
		-- Preparation
		source_items = source_multilist.items
		receiver_items_array = dest_multilist.items

		selection_index_array = source_multilist.selection as array
		reverse_index_array = for i=selection_index_array.count to 1 by -1 collect selection_index_array[i]
		selection_items_array = #()
		for i in selection_index_array do
		(
			append selection_items_array source_items[i]
		)

		-- Append
		join receiver_items_array selection_items_array
		dest_multilist.items = receiver_items_array

		-- Remove
		for i in reverse_index_array do
		(
			deleteItem source_items i
		)
		source_multilist.items = source_items
	)

	fn node_to_name the_node =
	(
		handle = the_node.handle
		obj_name = the_node.name
		handle_name = obj_name + "<" + handle as string + ">"
		return handle_name
	)

	fn updateContainer =
	(
		-- Collate all the nodes via name
		current_obj_selection = lb_con_object.items
		current_light_selection = lb_con_lights.items
		current_camera_selection = lb_con_camera.items
		current_tycache_selection = lb_con_tycache.items

		current_all_selection = #()
		current_node_selection = #()

		for i in current_obj_selection do
		(
			append current_all_selection i
			current_node = getNodeByName i
			append current_node_selection current_node
		)
		for i in current_light_selection do
		(
			append current_all_selection i
			current_node = getNodeByName i
			append current_node_selection current_node
		)
		for i in current_camera_selection do
		(
			append current_all_selection i
			current_node = getNodeByName i
			append current_node_selection current_node
		)
		for i in current_tycache_selection do
		(
			append current_all_selection i
			current_node = getNodeByName i
			append current_node_selection current_node
		)

		-- if current_all_selection.count == 0 do return False

		-- ayon_data = selection[1].modifiers[1]
		select current_self
		IsolateSelection.ExitIsolateSelectionMode()
		ayon_data = current_modifier
		ayon_data.sel_list = #()

		temp_arr = #()
		i_node_arr = #()
		for c in current_node_selection do
		(
			handle_name = node_to_name c
			node_ref = NodeTransformMonitor node:c
			name = c as string
			append temp_arr handle_name
			append i_node_arr node_ref
			append ayon_data.sel_list name
		)
		ayon_data.all_handles = i_node_arr
		ayon_data.AYONparams.list_node.items = temp_arr
	)
	
	fn double_click_functionality ui_object sel =
	(
		check_selection = selection[1]
		current_node = getNodeByName ui_object.items[sel]
		
		if check_selection == current_node then
		(
			select current_self
			IsolateSelection.ExitIsolateSelectionMode()
		)
		else
		(
			select current_node
			IsolateSelection.EnterIsolateSelectionMode()
		)
	)
	
	fn right_click_functionality ui_object =
	(
		current_array = ui_object.selection as array
		if current_array.count == 0 and current_array != undefined then
		(
			return none
		)
		message = ""
		for i in current_array do
		(
			current_node = ui_object.items[i]
			message += ("Full Name: " + current_node + "\n")
		)
		messageBox message
	)

	/*--------------
	   CALLBACKS
	--------------*/
	on AyonContainerEdit open do
	(
		-- Grab current Container
		current_handles = selection[1].modifiers[1].all_handles
		current_self = selection[1]
		current_modifier = current_self.modifiers[1]

		-- Create a temp array with only included nodes
		current_container_node = #()
		for ref_handle in current_handles do
		(
			append current_container_node ref_handle.node
		)

		-- Create temp arrays
		scene_objs = #()
		scene_cameras = #()
		scene_lights = #()
		scene_tycache = #()
		container_objs = #()
		container_cameras = #()
		container_lights = #()
		container_tycache = #()

		-- Grab and filter all objects
		for obj in objects do
		(
			if classOf obj == container then
			(
				continue
			)

			found = findItem current_container_node obj

			if found > 0 then
			(
				-- It is in the container
				sortObjects obj &container_objs &container_cameras &container_lights &container_tycache
			)
			else
			(
				-- It is not in the container
				sortObjects obj &scene_objs &scene_cameras &scene_lights &scene_tycache
			)
		)

		-- Sort out the light targets
		sortLightTargets &container_lights &container_cameras
		sortLightTargets &scene_lights &scene_cameras

		lb_object.items = sort scene_objs
		lb_camera.items = sort scene_cameras
		lb_lights.items = sort scene_lights
		lb_tycache.items = sort scene_tycache

		lb_con_object.items = sort container_objs
		lb_con_camera.items = sort container_cameras
		lb_con_lights.items = sort container_lights
		lb_con_tycache.items = sort container_tycache
	)

	/*--------------
	   UI FUNCTIONS
	--------------*/
	on b_object_in pressed do
	(
		moveObjects &lb_object &lb_con_object
	)

	on b_object_out pressed do
	(
		moveObjects &lb_con_object &lb_object
	)

	on b_camera_in pressed do
	(
		moveObjects &lb_camera &lb_con_camera
	)

	on b_camera_out pressed do
	(
		moveObjects &lb_con_camera &lb_camera
	)

	on b_light_in pressed do
	(
		moveObjects &lb_lights &lb_con_lights
	)

	on b_light_out pressed do
	(
		moveObjects &lb_con_lights &lb_lights
	)

	on b_tycache_in pressed do
	(
		moveObjects &lb_tycache &lb_con_tycache
	)

	on b_tycache_out pressed do
	(
		moveObjects &lb_con_tycache &lb_tycache
	)
	
	on lb_object doubleClicked sel do
	(
		double_click_functionality lb_object sel
	)
	
	on lb_object rightClick do
	(
		right_click_functionality lb_object
	)
	
	on lb_camera doubleClicked sel do
	(
		double_click_functionality lb_camera sel
	)
	
	on lb_camera rightClick do
	(
		right_click_functionality lb_camera
	)
	
	on lb_lights doubleClicked sel do
	(
		double_click_functionality lb_lights sel
	)
	
	on lb_lights rightClick do
	(
		right_click_functionality lb_lights
	)
	
	on lb_tycache doubleClicked sel do
	(
		double_click_functionality lb_tycache sel
	)
	
	on lb_tycache rightClick do
	(
		right_click_functionality lb_tycache
	)

	on lb_con_object doubleClicked sel do
	(
		double_click_functionality lb_con_object sel
	)
	
	on lb_con_object rightClick do
	(
		right_click_functionality lb_con_object
	)
	
	on lb_con_camera doubleClicked sel do
	(
		double_click_functionality lb_con_camera sel
	)
	
	on lb_con_camera rightClick do
	(
		right_click_functionality lb_con_camera
	)
	
	on lb_con_lights doubleClicked sel do
	(
		double_click_functionality lb_con_lights sel
	)
	
	on lb_con_lights rightClick do
	(
		right_click_functionality lb_con_lights
	)
	
	on lb_con_tycache doubleClicked sel do
	(
		double_click_functionality lb_con_tycache sel
	)
	
	on lb_con_tycache rightClick do
	(
		right_click_functionality lb_con_tycache
	)

	on b_accept pressed do
	(
		updateContainer()
		destroyDialog AyonContainerEdit
	)

	on b_cancel pressed do
	(
		select current_self
		IsolateSelection.ExitIsolateSelectionMode()
		destroyDialog AyonContainerEdit
	)
)"""
