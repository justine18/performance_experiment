using JuMP
using JSON
using DataFrames
using BenchmarkTools
using Gurobi

function read_tuple_list(filename)
    return [tuple(x...) for x in JSON.parsefile(filename)]
end

function read_fixed_data()
    N = open(JSON.parse, "supply_chain/data/data_N.json")
    return N
end

function read_variable_data(n)
    IK = read_tuple_list("supply_chain/data/data_IK_$n.json")
    IL = read_tuple_list("supply_chain/data/data_IL_$n.json")
    IM = read_tuple_list("supply_chain/data/data_IM_$n.json")
    IJK = read_tuple_list("supply_chain/data/data_IJK_$n.json")
    IKL = read_tuple_list("supply_chain/data/data_IKL_$n.json")
    ILM = read_tuple_list("supply_chain/data/data_ILM_$n.json")
    d = read_tuple_list("supply_chain/data/data_D_$n.json")
    D = Dict()
    for x in d
        D[(x[1], x[2])] = x[3]
    end
    return IK, IL, IM, IJK, IKL, ILM, D
end

function intuitive_jump(IK, IL, IM, IJK, IKL, ILM, D, solve)
    model = Model()

    @variable(model, x[IJK] >= 0)
    @variable(model, y[IKL] >= 0)
    @variable(model, z[ILM] >= 0)

    @constraint(model, production[(i, k) in IK], sum(
        x[(i, j, k)] for (ii, j, kk) in IJK if ii == i && kk == k
    ) >= sum(y[(i, k, l)] for (ii, kk, l) in IKL if ii == i && kk == k)
    )

    @constraint(model, transport[(i, l) in IL], sum(
        y[(i, k, l)] for (ii, k, ll) in IKL if ii == i && ll == l
    ) >= sum(z[(i, l, m)] for (ii, ll, m) in ILM if ii == i && ll == l))

    @constraint(model, demand[(i, m) in IM], sum(
        z[(i, l, m)] for (ii, l, mm) in ILM if ii == i && mm == m
    ) >= D[i, m])

    # write_to_file(model, "int.lp")

    if solve == "True"
        set_silent(model)
        set_optimizer(model, Gurobi.Optimizer)
        set_time_limit_sec(model, 0)
        optimize!(model)
    end
end

function jump(I, L, M, IJ, JK, IK, KL, LM, D, solve)
    model = if solve == "True"
        direct_model(Gurobi.Optimizer())
    else
        Model()
    end

    set_string_names_on_creation(model, false)

    x_list = [
        (i, j, k)
        for (i, j) in IJ
        for (jj, k) in JK if jj == j
        for (ii, kk) in IK if ii == i && kk == k
    ]

    y_list = [
        (i, k, l)
        for i in I
        for (k, l) in KL
    ]

    z_list = [(i, l, m) for i in I for (l, m) in LM]

    @variable(model, x[x_list] >= 0)
    @variable(model, y[y_list] >= 0)
    @variable(model, z[z_list] >= 0)

    for (i, k) in IK
        @constraint(model,
            sum(
                x[(i, j, k)]
                for (ii, j) in IJ if ii == i
                for (jj, kk) in JK if jj == j && kk == k
            ) >= sum(y[(i, k, l)] for (kk, l) in KL if kk == k)
        )
    end

    for i in I, l in L
        @constraint(model,
            sum(y[(i, k, l)] for (k, ll) in KL if ll == l) >=
            sum(z[(i, l, m)] for (ll, m) in LM if ll == l))
    end

    for i in I, m in M
        @constraint(model, sum(z[(i, l, m)] for (l, mm) in LM if mm == m) >= D[i, m])
    end

    if solve == "True"
        set_silent(model)
        set_time_limit_sec(model, 0)
        optimize!(model)
    end
end

# solve = false
# samples = 2
# evals = 1
# time_limit = 5

solve = ARGS[1]
samples = parse(Int64, ARGS[2])
evals = parse(Int64, ARGS[3])
time_limit = parse(Int64, ARGS[4])

N = read_fixed_data()

t = DataFrame(I=Int[], Language=String[], MinTime=Float64[], MeanTime=Float64[], MedianTime=Float64[])
tt = DataFrame(I=Int[], Language=String[], MinTime=Float64[], MeanTime=Float64[], MedianTime=Float64[])

for n in N
    IK, IL, IM, IJK, IKL, ILM, D = read_variable_data(n)

    # if maximum(t.MinTime; init=0) < time_limit
    #     r = @benchmark jump($I, $L, $M, $IJ, $JK, $IK, $KL, $LM, $D, $solve) samples = samples evals = evals
    #     push!(t, (n, "JuMP", minimum(r.times) / 1e9, mean(r.times) / 1e9, median(r.times) / 1e9))
    #     println("JuMP done $n in $(round(minimum(r.times) / 1e9, digits=2))s")
    # end

    if maximum(tt.MinTime; init=0) < time_limit
        rr = @benchmark intuitive_jump($IK, $IL, $IM, $IJK, $IKL, $ILM, $D, $solve) samples = samples evals = evals
        push!(tt, (n, "Intuitive JuMP", minimum(rr.times) / 1e9, mean(rr.times) / 1e9, median(rr.times) / 1e9))
        println("Intuitive JuMP done $n in $(round(minimum(rr.times) / 1e9, digits=2))s")
    end
end

if solve == "True"
    file = "supply_chain/results/jump_results_solve.json"
    file2 = "supply_chain/results/intuitive_jump_results_solve.json"
else
    file = "supply_chain/results/jump_results_model.json"
    file2 = "supply_chain/results/intuitive_jump_results_model.json"
end

open(file, "w") do f
    JSON.print(f, t, 4)
end

open(file2, "w") do f
    JSON.print(f, tt, 4)
end

println("JuMP done")
